import argparse
import logging
import os

import zmq

import measurement_event_manager.util.logger as mem_logging

import samsguideclient as sgc


###############################################################################
## Sam's Guide Client
###############################################################################


def launch_client():
	'''Start up a Guide Client instance
	'''

	## Command-line arguments

	parser = argparse.ArgumentParser()
	parser.add_argument("config",
						help="Config file containing generation parameters",
						nargs="*")
	parser.add_argument("--endpoint",
						help="Endpoint address for MEM server connection",
						default="tcp://localhost:9010")
	parser.add_argument("--interactive", "-i",
						help="Enable interactive mode",
						action="store_true")
	cmd_args = parser.parse_args()


	## Setup
	########

	## Logging

	logger = logging.getLogger("SamsGuideClient")
	logger = mem_logging.quick_config(logger,
									  console_log_level=logging.INFO,
									  file_log_level=logging.DEBUG,
									  )
	logger.debug("Logging initialized.")


	## ZMQ messaging
	context = zmq.Context()


	## Guide client
	###############

	## Instantiate object
	guide_client = sgc.GuideClient.GuideClient(
										logger=logger,
										context=context,
										)
	guide_client.connect_to_server(endpoint=cmd_args.endpoint)

	
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
