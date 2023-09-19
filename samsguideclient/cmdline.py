import argparse
import logging
import os

import zmq

import measurement_event_manager.util.log as mem_logging
from measurement_event_manager.interfaces.guide import (
	GuideRequestInterface,
)

import samsguideclient as sgc


###############################################################################
## Default values
###############################################################################


DEF_GUIDE_ENDPOINT = "tcp://localhost:9010"


###############################################################################
## Sam's Guide Client
###############################################################################


def launch_client():
	'''Start up a Guide Client instance
	'''

	## Command-line arguments

	parser = argparse.ArgumentParser()
	parser.add_argument("config",
						help="Config file(s) containing generation parameters",
						nargs="*")
	parser.add_argument("--endpoint",
						help="Endpoint address for MEM server connection",
						default=None)
	parser.add_argument("--interactive", "-i",
						help="Enable interactive mode",
						action="store_true")
	parser.add_argument("--console-log-level",
						help="Logging level for console output",
						default="info")
	parser.add_argument("--file-log-level",
						help="Logging level for file output",
						default="info")
	cmd_args = parser.parse_args()


	## Setup
	########

	## Logging

	logger = logging.getLogger("SamsGuideClient")
	logger = mem_logging.quick_config(
				logger,
				console_log_level=mem_logging.parse_log_level(
												cmd_args.console_log_level
												),
				file_log_level=mem_logging.parse_log_level(
												cmd_args.file_log_level
												),
				)
	logger.debug("Logging initialized.")


	## Communications setup
	#######################


	## Initialize context
	context = zmq.Context()

	## Guide request address
	if cmd_args.endpoint is not None:
		guide_request_endpoint = cmd_args.guide_request_endpoint
	else:
		guide_request_endpoint = DEF_GUIDE_ENDPOINT


	## Guide client
	###############


	## Instantiate Guide client
	guide_client = sgc.sgc.GuideClient(
									endpoint=guide_request_endpoint,
									logger=logger,
									zmq_context=context,
									)

	
	## Argument-based execution
	###########################

	## If available, add the specified config as a measurement
	if cmd_args.config:
		for config_file in cmd_args.config:
			guide_client.add_from_file(os.getcwd(), config_file)


	## Interactive mode
	###################

	if cmd_args.interactive:
		sgc.sgcsh.GuideClientShell(guide_client).cmdloop()


if __name__ == "__main__":
	launch_client()
