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
	print_str += f"Meas type   : {mp.measurement_type}\n"
	# print_str += f"Start time  : {mp.start_time}\n"
	# print_str += f"End time    : {mp.end_time}\n"
	print_str += f"Setvals:\n"
	for instr_name, instr_vals in mp.setvals.items():
		print_str += f"--> {instr_name}:\n"
		for param_name, param_val in instr_vals.items():
			print_str += f"      {param_name:-<20}: {param_val}\n"

	## Footer
	print_str += "="*59
	print_str += "\n"

	return print_str
