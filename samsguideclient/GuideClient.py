"""
OOP interface for Sam's Guide Client
"""

import os

import himl
import zmq

from measurement_event_manager import MeasurementParams


###############################################################################
## Definitions and constants
###############################################################################


## Messaging protocol constants
DEFAULT_ENDPOINT = "tcp://localhost:9010"
DEFAULT_TIMEOUT = 2500 # in ms
PROTOCOL = "MEM-GR/0.1"


def load_config(base_dir, config_path):
	"""Load a himl config, starting at base_dir and moving through config_path
	"""
	cfg = himl.ConfigProcessor().process(
					cwd=base_dir,
					path=os.path.join(base_dir, config_path),
					type_strategies=[(list, ["override"]),
									 (dict, ["merge"])])
	return cfg


###############################################################################
## GuideClient class
###############################################################################


class GuideClient:
	"""An inteface class for a MEM Guide Client
	"""

	def __init__(self, logger, context=None):

		## Set up logging
		self.logger = logger

		## Set up ZMQ
		if context is not None:
			self._context = context
		else:
			self._context = zmq.Context()
		## Force the client to connect manually
		self.default_endpoint = DEFAULT_ENDPOINT
		self.socket = None


	## Connection
	#############


	def connect_to_server(self, endpoint=None):
		self.logger.debug("Creating socket")
		self.socket = self._context.socket(zmq.REQ)
		self.socket.setsockopt(zmq.RCVTIMEO, DEFAULT_TIMEOUT)
		if endpoint is None:
			endpoint = self.default_endpoint
		self.logger.info(f"Connecting to server at {endpoint}")
		self.socket.connect(endpoint)
		self.logger.info("Connected to server.")


	## Generic request-reply
	########################


	def send_request(self, request):
		"""Send a request, returning the reply
		"""

		## Make sure we have an open socket!
		if (self.socket is None) or (self.socket.closed):
			self.logger.warning("Socket has not been initialized or is closed;"
								" aborting.")
			return None

		## Wrap the request properly in the protocol envelope
		request_wrapped_raw = [PROTOCOL] + request
		## Encode everything into binary
		request_wrapped = [rr.encode() for rr in request_wrapped_raw]

		## Send the request
		self.logger.debug("Sending request...")
		self.logger.debug(request_wrapped)
		self.socket.send_multipart(request_wrapped)
		self.logger.debug("Request sent.")

		## Wait for a reply
		self.logger.debug("Awaiting reply...")
		try:
			reply_wrapped = self.socket.recv_multipart()
		except zmq.error.Again:
			self.logger.warning("Request timeout; no reply received.")
			self.logger.warning("Closing socket; needs to be reconnected.")
			self.socket.close()
			return None
		self.logger.info("Reply received:")
		self.logger.info(reply_wrapped)

		## Get the content from the reply - the protocol doesn't really give us
		## any information, as even an error will be returned with the same
		## protocol
		reply_binary = reply_wrapped[1:]
		## Decode the content from binary
		reply = [rr.decode() for rr in reply_binary]
		## Return the reply content
		return reply


	## Measurement load and config
	##############################


	def add_from_file(self, base_dir, config_path):
		"""Parse a config file to add a measurement
		"""
		## Load config using himl consolidation
		self.logger.debug(f"Loading from file: {config_path}")
		self.logger.debug(f"himl base_dir is {base_dir}")
		config = load_config(base_dir, config_path)
		## Generate a MeasurementParams object from the config
		## Even though technically we could pass the config directly to the
		## server as text without creating and serializing the MP object, we
		## can use this to ensure that the config is valid on the client side
		self.logger.debug("Creating MeasurementParams object...")
		measurement_params = MeasurementParams.MeasurementParams(**config)
		## Make the addition API call
		self.logger.debug("Sending measurement to server...")
		self.send_add(measurement_params)


	## MEM-GR interface
	###################


	## IDN - identification

	def send_idn(self, *args):
		"""Send an identification (IDN) query
		"""
		request = ["IDN",]
		reply = self.send_request(request)
		return reply


	## ADD - Addition to queue

	def send_add(self, measurement, *args):
		"""ADD a measurement to the queue
		"""
		request = ["ADD", measurement.to_json()]
		reply = self.send_request(request)
		return reply


	## RMV - Removal from queue

	def send_remove(self, index, *args):
		"""ReMoVe a measurement from the queue
		"""
		request = ["RMV"]
		if index:
			request.append(str(index))
		## Sending just the header will induce server-defined default behaviour
		reply = self.send_request(request)
		return reply
	

	## QUE - Queue content query

	def send_query(self, *args):
		"""QUEry the measurement queue
		"""
		request = ["QUE",]
		reply = self.send_request(request)
		return reply


	## FCH - Fetch counter change or query

	def send_fetch(self, counter, *args):
		"""Set the number of measurements to be FetCHed from the queue
		"""
		request = ["FCH"]
		## If the counter is not int-able, treat it as a query
		try:
			request.append(str(int(counter)))
		except ValueError:
			pass
		reply = self.send_request(request)
		return reply

