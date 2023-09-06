"""
Interactive shell for Sam's Guide Client for MEM
"""

import cmd


###############################################################################
## GuideClientShell
###############################################################################


class GuideClientShell(cmd.Cmd):
	"""An interactive shell interface for a MEM Guide Client
	"""

	## Class attributes from the example in the Python docs
	intro = "Measurement client interactive mode.\n"
	prompt = "[sgc] "
	file = None


	def __init__(self, guide_client, *args, **kwargs):
		self.guide_client = guide_client
		super().__init__(*args, **kwargs)


	## Cmd method overrides
	#######################


	def emptyline(self):
		## Do nothing when an empty line is returned, instead of the default
		## behaviour which is to repeat the last command.
		pass


	## Command functions
	####################


	def do_connect(self, *args):
		"""Connect to the specified endpoint
		"""
		endpoint = args[0] if args[0] else None
		self.guide_client.connect_to_server(endpoint=endpoint)


	def do_exit(self, *args):
		return True

