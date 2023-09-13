import argparse
import logging
import os

import zmq

import measurement_event_manager.util.log as mem_logging

import samsguideclient as sgc


###############################################################################
## Utility functions
###############################################################################

## Log level string/value parsing

STR2LOG = {
	"debug": logging.DEBUG,
	"info": logging.INFO,
	"warning": logging.WARNING,
	"error": logging.ERROR,
}

def parse_log_level(level_str_or_int):
	"""Parse a logging level, either as an int or as a string corresponding
	to a log level from the logging stdlib
	"""
	## Check if this is one of the predefined levels
	if level_str_or_int in STR2LOG:
		return STR2LOG[level_str_or_int]
	
	## Otherwise, try and parse it as an int
	try:
		level = int(level_str_or_int)
	except ValueError as e:
		raise ValueError(f"Cannot parse {level_str_or_int} as a logging"
						 " level") from e


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
				console_log_level=parse_log_level(cmd_args.console_log_level),
				file_log_level=parse_log_level(cmd_args.file_log_level),
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
