import logging

import zmq

import measurement_event_manager.util.logger as mem_logging

import samsguideclient as sgc


###############################################################################
## Sam's Guide Client
###############################################################################


def launch_client():
	'''Start up a Guide Client instance
	'''

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

	## Interactive mode
	if True:
		sgc.sgcsh.GuideClientShell(guide_client).cmdloop()


if __name__ == "__main__":
	launch_client()
