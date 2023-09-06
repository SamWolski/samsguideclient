import samsguideclient as sgc


###############################################################################
## Sam's Guide Client
###############################################################################


def launch_client():
	'''Start up a Guide Client instance
	'''

	## Guide client
	###############

	## Instantiate object
	guide_client = sgc.GuideClient.GuideClient()

	## Interactive mode
	if True:
		sgc.sgcsh.GuideClientShell(guide_client).cmdloop()


if __name__ == "__main__":
	launch_client()
