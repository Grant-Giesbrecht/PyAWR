import h5py
import time
import json
import numpy as np
from colorama import Fore, Style

def lin_to_dB(x:float, use10:bool=False):
	''' Converts a value from dB to linear units'''
	
	if use10:
		return 10*np.log10(x)
	else:
		return 20*np.log10(x)

def dB_to_lin(x:float, use10:bool=False):
	''' Converts a value from dB to linear units'''
	
	if use10:
		return 10**(x/10)
	else:
		return 10**(x/20)


# def dict_to_hdf(root_data:dict, save_file:str, use_json_backup:bool=True) -> bool:
# 	''' Writes a dictionary to an HDF file per the rules used by 'write_level()'. 
	
# 	* If the value of a key in another dictionary, the key is made a group (directory).
# 	* If the value of the key is anything other than a dictionary, it assumes
# 	  it can be saved to HDF (such as a list of floats), and saves it as a dataset (variable).
	
# 	'''
	
# 	def write_level(fh:h5py.File, level_data:dict):
# 		''' Writes a dictionary to the hdf file.
		
# 		Recursive function used by  '''
		
# 		# Scan over each directory of root-data
# 		for k, v in level_data.items():
			
# 			# If value is a dictionary, this key represents a directory
# 			if type(v) == dict:
				
# 				# Create a new group
# 				fh.create_group(k)
				
# 				# Write the dictionary to the group
# 				write_level(fh[k], v)
					
# 			else: # Otherwise try to write this datatype (ex. list of floats)
				
# 				# Write value as a dataset
# 				fh.create_dataset(k, data=v)
	
# 	# Start timer
# 	t0 = time.time()
	
# 	# Open HDF
# 	hdf_successful = True
# 	exception_str = ""
	
# 	# Recursively write HDF file
# 	with h5py.File(save_file, 'w') as fh:
		
# 		# Try to write dictionary
# 		try:
# 			write_level(fh, root_data)
# 		except Exception as e:
# 			hdf_successful = False
# 			exception_str = f"{e}"
	
# 	# Check success condition
# 	if hdf_successful:
# 		print(f"Wrote file in {time.time()-t0} sec.")
		
# 		return True
# 	else:
# 		print(f"Failed to write HDF file! ({exception_str})")
		
# 		# Write JSON as a backup if requested
# 		if use_json_backup:
			
# 			# Add JSON extension
# 			save_file_json = save_file[:-3]+".json"
			
# 			# Open and save JSON file
# 			try:
# 				with open(save_file_json, "w") as outfile:
# 					outfile.write(json.dumps(root_data, indent=4))
# 			except Exception as e:
# 				print(f"Failed to write JSON backup: ({e}).")
# 				return False
		
# 		return True

# def hdf_to_dict(filename, to_lists:bool=True) -> dict:
# 	''' Reads a HDF file and converts the data to a dictionary '''
	
# 	def read_level(fh:h5py.File) -> dict:
		
# 		# Initialize output dict
# 		out_data = {}
		
# 		# Scan over each element on this level
# 		for k in fh.keys():
			
# 			# Read value
# 			if type(fh[k]) == h5py._hl.group.Group: # If group, recusively call
# 				out_data[k] = read_level(fh[k])
# 			else: # Else, read value from file
# 				out_data[k] = fh[k][()]
				
# 				# Converting to a pandas DataFrame will crash with
# 				# some numpy arrays, so convert to a list.
# 				if type(out_data[k]) == np.ndarray and to_lists:
# 						out_data[k] = list(out_data[k])
# 				elif type(out_data[k]) == list and not to_lists:
# 						out_data[k] = np.array(out_data[k])
						
# 		return out_data
	
# 	# Open file
# 	with h5py.File(filename, 'r') as fh:
		
# 		try:
# 			root_data = read_level(fh)
# 		except Exception as e:
# 			print(f"Failed to read HDF file! ({e})")
# 			return None
	
# 	# Return result
# 	return root_data

def dict_summary(x:dict, verbose:int=0, indent_level:int=0, indent_char:str="   "):
	'''
	'''
	
	color_dict = Fore.CYAN
	color_name = Fore.GREEN
	color_lines = Fore.LIGHTBLACK_EX
	color_list_type = Fore.MAGENTA
	color_type = Fore.YELLOW
	color_value = Fore.WHITE
	color_ellips = Fore.RED
	
	lvlmarker_1 = "|"
	lvlmarker_2 = "."
	
	def get_indent(indent_level:int):
		
		indent_char0 = f" {indent_char}"
		indent_char1 = f"{lvlmarker_1}{indent_char}"
		indent_char2 = f"{lvlmarker_2}{indent_char}"
		
		indent_str = ""
		for i in range(indent_level):
			if i == 0:
				indent_str += indent_char0
			elif i % 2 == 1:
				indent_str += indent_char1
			else:
				indent_str += indent_char2
		return f"{color_lines}{indent_str}{Style.RESET_ALL}"
	
	def value_to_string(val, verbose:int, indent_level, length_limit:int=50, wrap_length:int=80):
		
		# Get full value string if verbose != 0
		if verbose == 0:
			return ""
		
		val_str = f"{val}"
		
		# If verbose == 1, truncate
		if verbose == 1:
			if len(val_str) > length_limit:
				val_str = val_str[:length_limit//2] + f"{color_ellips}...{color_value}" + val_str[-(length_limit//2-3):]
		
		# If verbose == 2, indent and print full value
		if verbose == 2:
			
			# Get length of color specifier
			cvlen = len(color_value)
			
			# Get indent char
			indent = get_indent(indent_level+1)
			indent.replace('\t', "    ")
			
			# Initialize with newline, indent and color
			if type(val) == str:
				val_str = f"\n{indent}{color_value}\"{val_str}\""
			else:
				val_str = f"\n{indent}{color_value}{val_str}"
			val_str.replace('\t', "    ")
			
			# Find last newline
			nlidx = val_str.rfind('\n')
			
			# Continue to wrap line until under length limit
			while len(val_str) - nlidx - cvlen > wrap_length:
				
				# Add newline (and color specs)
				val_str = val_str[:(nlidx)+wrap_length+cvlen] + "\n" + indent + color_value + val_str[(nlidx)+wrap_length+cvlen:]
				
				# Find new index
				nlidx = val_str.rfind('\n')
		
		else:
			# Add color to string
			if type(val) == str:
				val_str = f"{color_value}\"{val_str}\"{Style.RESET_ALL}"
			else:
				val_str = f"{color_value}{val_str}{Style.RESET_ALL}"
		
		return val_str
	
	# Scan over each key
	for k in x.keys():
		
		# IF key points to dictionary, recursive call
		if type(x[k]) == dict:
			print(f"{get_indent(indent_level)}[{color_dict}{k}{Style.RESET_ALL}]")
			dict_summary(x[k], verbose=verbose, indent_level=indent_level+1)
			
		# Otherwise print data element stats
		else:
			val = x[k]
			
			if type(val) == list:
				try:
					val0 = val[0]
				except:
					val0 = None
				
				if type(val0) == list:
					val_str = value_to_string(val, verbose, indent_level)
					print(f"{get_indent(indent_level)}{color_name}{k}{Style.RESET_ALL} = {color_list_type}{type(val)}{Style.RESET_ALL}, {len(val)} x {color_list_type}{type(val0)} {val_str}{Style.RESET_ALL}")
				else:
					val_str = value_to_string(val, verbose, indent_level)
					print(f"{get_indent(indent_level)}{color_name}{k}{Style.RESET_ALL} = {color_list_type}{type(val)}{Style.RESET_ALL}, {len(val)} x {color_type}{type(val0)} {val_str}{Style.RESET_ALL}")
			else:
				val_str = value_to_string(val, verbose, indent_level)
				print(f"{get_indent(indent_level)}{color_name}{k}{Style.RESET_ALL} = {color_type}{type(val)}{Style.RESET_ALL} {val_str}{Style.RESET_ALL}")