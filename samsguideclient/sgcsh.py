"""
Interactive shell for Sam's Guide Client for MEM
"""

import cmd
import os


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


	## Server-related functions


	def do_connect(self, endpoint):
		"""Connect to the specified endpoint
		"""
		## TODO perhaps find a more elegant way of handling empty strings
		endpoint = endpoint if endpoint else None
		self.guide_client.connect_to_server(endpoint=endpoint)


	## Messaging and requests


	def do_idn(self, args):
		"""Send an identification (IDN) query
		"""
		self.guide_client.send_idn()


	def do_add(self, config_path):
		"""Add a measurement to the queue using the specified config file(s)
		"""
		self.guide_client.add_from_file(base_dir=os.getcwd(),
										config_path=config_path)
		
	
	def do_remove(self, index):
		"""Remove a measurement from the queue
		"""
		self.guide_client.send_remove(index)


	def do_query(self, args):
		"""Query the queue contents
		"""
		self.guide_client.send_query()


	## Shell functions


	def do_exit(self, args):
		return True

