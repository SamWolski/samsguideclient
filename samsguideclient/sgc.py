"""
OOP interface for Sam's Guide Client
"""

import collections
import logging
import os
import sys

import himl
import zmq

from measurement_event_manager import measurement_params
from measurement_event_manager.util import log as mem_logging
from measurement_event_manager.interfaces.guide import (
	GuideRequestInterface,
)

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

	def __init__(self, endpoint,
		logger=None,
		zmq_context=None
		):

		## Set up logging
		if logger is None:
			logger = logging.getLogger(__name__)
			self.logger = mem_logging.quick_config(
											logger,
											console_log_level=logging.INFO,
											file_log_level=None,
											)
		else:
			self.logger = logger

		## ZMQ messaging attributes
		self._endpoint = endpoint
		if zmq_context is None:
			self._context = zmq.Context()
		else:
			self._context = zmq_context
		
		## Initialize the interface
		## Starts with an empty socket - will be added when connecting
		self._interface = GuideRequestInterface(
											socket=None,
											protocol_name="MEM-GR/0.1",
											logger=self.logger,
											)
		## Set up connection
		## Automatic the first time; reconnects must be manual
		## Socket is passed to the interface as part of the connection method
		self.connect_to_server()


	## Server functionality and status
	##################################


	## Connection

	def connect_to_server(self, endpoint=None):
		"""Connect to the serverat the specified endpoint
		"""
		## If a new endpoint is specified, update the stored one
		if endpoint is not None:
			self._endpoint = endpoint
		## (Re)open the socket
		guide_request_socket = self._context.socket(zmq.REQ)
		guide_request_socket.connect(self._endpoint)
		self.logger.debug(f"Guide request socket bound to {self._endpoint}")
		## Update the socket at the interface
		self._interface.set_socket(guide_request_socket)
		## Exit gracefully
		return True


	## General

	def get_server_identity(self):
		"""Query the identity of the server
		"""
		server_idn = self._interface.idn()
		return server_idn


	## Fetch counter

	def set_fetch_counter(self, new_value: int):
		"""Set the fetch counter of the server queue
		"""
		counter = self._interface.set_counter(new_value)
		self.logger.info(f"Fetch counter set to {counter}")
		return counter


	def get_fetch_counter(self):
		"""Query the value of the fetch counter of the server queue
		"""
		counter = self._interface.get_counter()
		self.logger.info(f"Fetch counter is {counter}")
		return counter


	## Measurement load and config
	##############################


	## Add

	def add_from_file(self, base_dir, config_path):
		"""Parse a config file to add a measurement
		"""
		## Load config using himl consolidation
		self.logger.debug(f"Loading from file: {config_path}")
		self.logger.debug(f"himl base_dir is {base_dir}")
		config = load_config(base_dir, config_path)
		## Add the measurement based on the loaded config
		self.add_from_dict(config)

		
	def add_from_dict(self, params_dict):
		"""Add a measurement to the queue from a dict-based config
		"""
		## Generate a MeasurementParams object from the config
		## Even though technically we could pass the config directly to the
		## server as text without creating and serializing the MP object, we
		## can use this to ensure that the config is valid on the client side
		self.logger.debug("Creating MeasurementParams object...")
		params = measurement_params.MeasurementParams(**params_dict)
		## Make the addition API call
		self.logger.debug("Sending measurement to server...")
		self._interface.add(params)


	## Queue

	def get_queue_len(self):
		"""Get the length of the server queue (number of measurements)
		"""
		return self._interface.len()


	def get_queue_contents(self):
		"""Request the current contents of the server queue
		"""
		## Get the queue contents as strings
		queue = self._interface.query()
		return queue


	def dump_queue_contents(self, target=None):
		"""Dump the current contents of the server queue to a writeable target
		"""
		## Get the contents of the queue
		queue_contents = self.get_queue_contents()
		print_list = []
		for index, mp in enumerate(queue_contents):
			print_list.append(pretty_print(mp, index=index))
		## TODO confirm that this will be lazy-evaluated only when used later
		print_generator = (f"{pp}\n" for pp in print_list)
		## Write to file-like object
		if target:
			with open(target, 'w') as target_handle:
				target_handle.writelines(print_generator)
		## Fall back on stdout
		else:
			sys.stdout.writelines(print_generator)


	## Remove

	def remove(self, index_iterable):
		## Create a list corresponding to the queue indices
		queue_len = self.get_queue_len()
		if queue_len == 0:
			self.logger.warning("Measurement queue is empty; cannot remove.")
			return
		queue_indices = list(range(queue_len))
		## For each entry in the index iterable, apply it as an index on the 
		## indices list, and append the resulting indices to the container
		resolved_indices = []
		for index_spec in index_iterable:
			## Apply python's indexing powers directly to the queue_indices
			new_indices = queue_indices[index_spec]
			## Check if the new indices are a singleton or list (when slicing)
			## to avoid ending up with some nested list elements
			if isinstance(new_indices, collections.abc.Sequence):
				resolved_indices.extend(new_indices)
			else:
				resolved_indices.append(new_indices)
		## We can make a set of the resolved indices, to unclutter the message
		## by removing potential duplicates
		index_list = list(set(resolved_indices))
		## Send the removal request
		removed_indices = self._interface.remove(index_list)
		self.logger.info(f"Successfully removed indices {removed_indices}")
		return removed_indices

