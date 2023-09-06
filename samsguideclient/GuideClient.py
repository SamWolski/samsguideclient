"""
OOP interface for Sam's Guide Client
"""

import zmq


###############################################################################
## Definitions and constants
###############################################################################


## Messaging protocol constants
DEFAULT_ENDPOINT = "tcp://localhost:9010"
DEFAULT_TIMEOUT = 2500 # in ms


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

