"""
Interactive shell for Sam's Guide Client for MEM
"""

import cmd
from importlib.metadata import version
import os

from measurement_event_manager.util.errors import ConnectionTimeoutError


def parse_index_int(index_str):
	"""Parse a string representing a numeric index, which may be empty
	"""
	## If the string is empty (eg when using open-ended slices), return None
	## for valid slice construction
	if index_str == "":
		return None
	return int(index_str)


###############################################################################
## GuideClientShell
###############################################################################


class GuideClientShell(cmd.Cmd):
	"""An interactive shell interface for a MEM Guide Client
	"""

	## Class attributes from the example in the Python docs
	intro = (
		"Measurement client interactive mode."
		f"\nVersion: {version('samsguideclient')}"
	)
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


	## Here, we override onecmd() in order to wrap any executed command
	## in a try-catch block looking for a ConnectionTimeoutError. 
	## This way, we don't have to clutter up the code for each individual
	## command definition, and commands that have nothing to do with sending
	## requests to the server will not be affected anyway.
	def onecmd(self, line):
		"""Interpret the argument as though it had been typed in response
		to the prompt.

		This may be overridden, but should not normally need to be;
		see the precmd() and postcmd() methods for useful execution hooks.
		The return value is a flag indicating whether interpretation of
		commands by the interpreter should stop.

		"""
		## Up until the next comment is the same as the original
		cmd, arg, line = self.parseline(line)
		if not line:
			return self.emptyline()
		if cmd is None:
			return self.default(line)
		self.lastcmd = line
		if line == 'EOF' :
			self.lastcmd = ''
		if cmd == '':
			return self.default(line)
		else:
			try:
				func = getattr(self, 'do_' + cmd)
			except AttributeError:
				return self.default(line)
			## Attempt to execute the command with custom exception handling
			try: 
				result = func(arg)
			except ConnectionTimeoutError:
				print("*** Connection timed out; command incomplete. ***")
			else:
				return result


	## Command functions
	####################


	## Server-related functions


	def do_connect(self, endpoint):
		"""Connect to the specified endpoint
		"""
		## TODO perhaps find a more elegant way of handling empty strings
		endpoint = endpoint if endpoint else None
		self.guide_client.connect_to_server(endpoint=endpoint)


	def do_fetch(self, new_value):
		"""Interact with the fetch counter of the server queue

		A single int argument will be used to set the value.
		Calling with no arguments will query the existing value.
		"""
		try:
			new_value = int(new_value)
		except ValueError:
			self.guide_client.get_fetch_counter()
		else:
			self.guide_client.set_fetch_counter(new_value)


	## Messaging and requests


	def do_idn(self, args):
		"""Send an identification (IDN) query
		"""
		self.guide_client.get_server_identity()


	def do_add(self, config_path):
		"""Add a measurement to the queue using the specified config file(s)
		"""
		try:
			self.guide_client.add_from_file(base_dir=os.getcwd(),
											config_path=config_path)
		except FileNotFoundError:
			print(f"Config file not found at {config_path}; "
		 		  "cannot process add request.")
		
	
	def do_remove(self, index_string):
		"""Remove a measurement from the queue

		Python's slicing syntax is supported using the : delimiter, eg 2:5
		"""
		## Default to removing the last element
		if index_string == "":
			index_string = "-1"
		index_list = index_string.split(" ")
		index_spec = []
		## Parse different items supplied
		for index_str in index_list:
			## Ranges using : syntax
			if index_str.count(":") == 2:
				start, stop, step = index_str.split(":")
				## We must be able to parse *all* of the components for the
				## slice to work, so it's okay to put everything inside the
				## same try block
				try:
					new_slice = slice(parse_index_int(start),
									  parse_index_int(stop),
									  parse_index_int(step))
				except ValueError:
					print(f"Index f{index_str} cannot be parsed")
					continue
				else:
					index_spec.append(new_slice)
			elif index_str.count(":") == 1:
				start, stop = index_str.split(":")
				## Same as above
				try:
					new_slice = slice(parse_index_int(start),
									  parse_index_int(stop))
				except ValueError:
					print(f"Index f{index_str} cannot be parsed")
					continue
				else:
					index_spec.append(new_slice)
			## Single scalar values
			else:
				try:
					new_index = int(index_str)
				except ValueError:
					print(f"Index f{index_str} cannot be parsed")
					continue
				else:
					index_spec.append(new_index)
		## API call with parsed values (ie *not* strings!)
		self.guide_client.remove(index_spec)


	def do_query(self, target):
		"""Query the queue contents and dump them to a writeable target

		Defaults to sys.stdout
		"""
		self.guide_client.dump_queue_contents(target)


	def do_len(self, args):
		"""Query the length of the server queue
		"""
		self.guide_client.get_queue_len()


	## Shell functions


	def do_exit(self, args):
		return True

