"""
Pretty-printing functionality for presenting MeasurementParams information
"""




###############################################################################
## Main pretty-print function
###############################################################################


def pretty_print(mp,
	index=None,
	):
	"""Print some or all of the information in the MeasurementParams object
	"""

	print_str = ""

	## Header
	if index is not None:
		print_str += f"== Index {index: <4}"
		print_str += "="*46
	else:
		print_str += "="*59
	print_str += "\n"

	## Body
	
	print_str += f"Submitter: {mp.submitter}\n"
	## Metadata
	print_str += f"Metadata:\n"
	for meta_key, meta_val in mp.metadata.items():
		print_str += f"    {meta_key:-<20}: {meta_val}\n"
	## Setvals
	print_str += f"Setvals:\n"
	for instr_name, instr_vals in mp.setvals.items():
		print_str += f"--> {instr_name}:\n"
		for param_name, param_val in instr_vals.items():
			print_str += f"      {param_name:-<20}: {param_val}\n"

	## Footer
	print_str += "="*59
	print_str += "\n"

	return print_str
