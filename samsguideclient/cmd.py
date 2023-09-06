import logging

import measurement_event_manager.util.logger as mem_logging

import samsguideclient as sgc


###############################################################################
## Sam's Guide Client
###############################################################################


def launch_client():
	'''Start up a Guide Client instance
	'''

	## Logging
	##########

	logger = logging.getLogger("SamsGuideClient")
	logger = mem_logging.quick_config(logger,
									  console_log_level=logging.INFO,
									  file_log_level=logging.DEBUG,
									  )
	logger.debug("Logging initialized.")


	## Guide client
	###############

	## Instantiate object
	guide_client = sgc.GuideClient.GuideClient()

	## Interactive mode
	if True:
		sgc.sgcsh.GuideClientShell(guide_client).cmdloop()


if __name__ == "__main__":
	launch_client()
