"""
OOP interface for Sam's Guide Client
"""

import os
import sys

import himl
import zmq

from measurement_event_manager import MeasurementParams

from samsguideclient.pretty_print import pretty_print


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


	def _send_request(self, request):
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
		self._send_add(measurement_params)


	def remove_measurement(self, index=None):
		"""Request the removal of a measurement from the server queue
		"""
		remove_status = self._send_remove(index)


	def get_queue_contents(self):
		"""Request the current contents of the server queue
		"""
		queue_reply = self._send_query()
		## The first element is the reply header, "QUE"
		return queue_reply[1:]


	def dump_queue_contents(self, target=None):
		"""Dump the current contents of the server queue to a writeable target
		"""
		## Get the contents of the queue
		queue_contents = self.get_queue_contents()
		print_list = []
		for index, mp_spec in enumerate(queue_contents):
			## Reconstruct the MeasurementParams object
			mp_obj = MeasurementParams.from_json(mp_spec)
			print_list.append(pretty_print(mp_obj, index=index))
		## TODO confirm that this will be lazy-evaluated only when used later
		print_generator = (f"{pp}\n" for pp in print_list)
		## Write to file-like object
		if target:
			with open(target, 'w') as target_handle:
				target_handle.writelines(print_generator)
		## Fall back on stdout
		else:
			sys.stdout.writelines(print_generator)


	def get_queue_len(self):
		"""Get the length of the server queue (number of measurements)
		"""
		len_reply = self._send_len()
		## The first element is the reply header, "LEN"
		return len_reply[1:]


	## Server functionality
	#######################

	## General

	def get_server_identity(self):
		"""Query the identity of the server
		"""
		server_idn = self._send_idn()
		return server_idn


	## Fetch counter

	def set_fetch_counter(self, new_value: int):
		"""Set the fetch counter of the server queue
		"""
		counter_value = self._send_fetch(new_value)
		self.logger.info(f"Fetch counter set to {counter_value}")
		return counter_value
	

	def get_fetch_counter(self):
		"""Query the value of the fetch counter of the server queue
		"""
		counter_value = self._send_fetch()
		self.logger.info(f"Fetch counter is {counter_value}")
		return counter_value


	## MEM-GR interface
	###################

	## NB These methods are part of the private interface of the class itself,
	## and should not be used as a public API!

	## IDN - identification

	def _send_idn(self):
		"""Send an identification (IDN) query
		"""
		request = ["IDN",]
		reply = self._send_request(request)
		return reply


	## ADD - Addition to queue

	def _send_add(self, measurement):
		"""ADD a measurement to the queue
		"""
		request = ["ADD", measurement.to_json()]
		reply = self._send_request(request)
		return reply


	## RMV - Removal from queue

	def _send_remove(self, index=None):
		"""ReMoVe a measurement from the queue
		"""
		request = ["RMV"]
		if index is not None:
			request.append(str(index))
		## Sending with no args will induce server-defined default behaviour
		reply = self._send_request(request)
		return reply
	

	## QUE - Queue content query

	def _send_query(self):
		"""QUEry the measurement queue
		"""
		request = ["QUE",]
		reply = self._send_request(request)
		return reply


	## LEN - Queue length query

	def _send_len(self):
		"""Check the LENgth of the queue
		"""
		request = ["LEN"]
		reply = self._send_request(request)
		return reply


	## FCH - Fetch counter change or query

	def _send_fetch(self, new_value=None):
		"""Set the number of measurements to be FetCHed from the queue
		"""
		## Construct request
		request = ["FCH"]
		if new_value is not None:
			request.append(str(int(new_value)))
		## Send request
		reply = self._send_request(request)
		## Process reply
		if reply[0] == "FCH":
			return reply[1]
		## TODO handle errors?

