import numpy as np
import datetime



def get_setup(file_name):

	col_constraints = []
	row_constraints = []
	with open(file_name) as f_link:

		def _parse_col_line(line):
			_parse_col_line_helper(line,col_constraints)

		def _parse_row_line(line):
			_parse_row_line_helper(line,row_constraints)

		parser = _parse_col_line

		for line in f_link:
			line = line.strip()
			if line == "-":
				parser = _parse_row_line
				continue

			parser(line)

	if not _validate_setup_data(col_constraints,row_constraints):
		raise Exception("Not Valid Input Data")

	return col_constraints,row_constraints

def _parse_col_line_helper(line,col_constraints):
	values = [ int(value) for value in line.split() ]

	if len(col_constraints) == 0:
		for _ in values:
			col_constraints.append( list() )

	for value,column in zip(values,col_constraints):
		column.append(value)

def _parse_row_line_helper(line,row_constraints):
	values = [ int(value) for value in line.split() ]

	row_constraints.append(values)


def _validate_setup_data(col_constraints,row_constraints):

	validate_list = []

	num_data_cols = len(col_constraints[0])
	num_data_rows = len(row_constraints[0])

	for column_data in col_constraints:
		is_valid = len(column_data) == num_data_cols
		validate_list.append(is_valid)

	for row_data in row_constraints:
		is_valid = len(row_data) == num_data_rows
		validate_list.append(is_valid)

	return all(validate_list)



def generate_valid_cell_group(group_data,group_size):

	valid_row_list = []

	if not any(group_data):
		# all zeros
		yield np.zeros(group_size,dtype=np.bool)


	segments = []
	for data in group_data:
		if data != 0:
			segments.append([True for _ in range(data)])

	padding_req = group_size - sum(group_data)

	num_padding_segments = len(segments) + 1

	for padding_config in padding_generator(num_padding_segments,padding_req):

		group = []

		padding_segments = []
		for padding_size in padding_config:
			padding_segments.append([False for _ in range(padding_size)])

		for index in range(len(segments)):
			group.extend(padding_segments[index])
			group.extend(segments[index])

		group.extend(padding_segments[-1])

		yield np.array(group,dtype=np.bool)


def padding_generator(num_padding_segments,padding_req):
	"""
	Note that inner values must be non-zero
	"""

	max_stack_size = num_padding_segments-1

	valid_values = list(reversed(range(padding_req+1)))

	stack = [ list(valid_values), ]

	while stack:

		while len(stack) < max_stack_size:
			stack.append( list(valid_values) )
			if len(stack) > 1:
				stack[-1].pop() # inner values can't be zero

		if len(stack) == max_stack_size:

			cur_values = [node[-1] for node in stack]
			cur_total = sum( cur_values )
			new_value = padding_req - cur_total

			if new_value >= 0:
				cur_values.append(new_value)
				if len(cur_values[1:-1]) == 0 or all(cur_values[1:-1]):
					yield tuple( cur_values)

		if len(stack) > 0 and len(stack[-1]) > 0:
			stack[-1].pop()

		while len(stack) > 0 and len(stack[-1]) == 0:
			stack.pop()
			if len(stack) > 0:
				stack[-1].pop()


def validate_cell_group(array,data_list):
	
	index = 0
	for data in data_list:
		if data == 0:
			continue

		count = 0

		while index < len(array) and not array[index]:
			index+=1

		while index < len(array) and array[index]:
			index+=1		
			count+=1

		if count != data:
			return False

	return True


def print_table(table,output_file_name=None,verbose=True):
	
	row_size = len(table[0])
	string_format = "".join([ "{{{ii}}}".format(ii=ii) for ii in range(row_size)])
	table_string_list = []
	for row in table:
		pretty_data = []
		for value in row:
			if value:
				pretty_data.append("*")
			else:
				pretty_data.append(" ")
		output_string = string_format.format(*tuple(pretty_data))
		table_string_list.append(output_string)

	table_string = "\n".join(table_string_list)

	if output_file_name is not None:
		with open(output_file_name,"w") as output_file:
			print>>output_file,table_string
	
	if verbose:
		print table_string



def calc_group_order(group_data):
	"""
	Calc order to fill in by:
	- Max value
	- Total Sum
	- Number of values
	"""

	meta_data = []

	index_field = 0
	max_field = 1
	sum_field = 2
	len_field = 3

	for index,data_list in enumerate(group_data):

		data_entry = (index,max(data_list),sum(data_list),len(data_list))

		meta_data.append(data_entry)

	max_max = max( data_entry[max_field] for data_entry in meta_data)
	sum_max = max( data_entry[sum_field] for data_entry in meta_data)
	len_max = max( data_entry[len_field] for data_entry in meta_data)

	# For data entries that require nothing
	for index,data_list in enumerate(group_data):
		if all( item==0 for item in data_list):
			meta_data[index] = (index,max_max,sum_max,len_max)

	meta_data.sort(key=lambda xx:xx[max_field])
	max_rankings = { data_entry[index_field]:rank for rank,data_entry in enumerate(meta_data) }

	meta_data.sort(key=lambda xx:xx[sum_field])
	sum_rankings = { data_entry[index_field]:rank for rank,data_entry in enumerate(meta_data) }

	meta_data.sort(key=lambda xx:xx[len_field])
	len_rankings = { data_entry[index_field]:rank for rank,data_entry in enumerate(meta_data) }

	order = range(len(group_data))

	def rank_value(index):
		"""
		We want the the groups (row or column) that have the highest
		of these values to be at the front of the list.
		"""
		value = max_rankings[index]**2 + sum_rankings[index]**2 + len_rankings[index]**2
		return -value

	order.sort(key=rank_value)
	return order


def solve(input_file_name,output_file_name="output.txt"):

	col_constraints,row_constraints = col_constraints, row_constraints = get_setup(input_file_name)

	num_cols = len(col_constraints)
	num_rows = len(row_constraints)

	row_size = num_cols
	col_size = num_rows

	temp_dict = {"count":0}

	display_interval = 10**4

	def count_callback():
		temp_dict["count"] +=1
		count = temp_dict["count"]
		if count > 0 and count%display_interval == 0 :
			print count

	def table_checker(table):
		count_callback()
		end_time = datetime.datetime.now()

		for row_array,row_data in zip(table,row_constraints):
			if not validate_cell_group(row_array,row_data):
				return False

		for col_array,col_data in zip(table.T,col_constraints):
			if not validate_cell_group(col_array,col_data):
				return False
		print_table(table,output_file_name)
		print "Done"
		print "Completed:{now}".format(now=end_time)
		print "Duration:{length}".format(length=end_time-start_time)
		exit()

	start_time = datetime.datetime.now()
	print ""
	print "Calculating Solution"
	print "Stated:{now}".format(now=start_time)
	print ""

	solver_helper_starter(num_rows,num_cols,row_constraints,col_constraints,table_checker)

	print "Search Completed" # This shouldn't print.


def solver_helper_starter(num_rows,num_cols,row_constraints,col_constraints,table_checker_callback):
	row_size = num_cols
	col_size = num_rows
	rows_active = np.zeros(num_rows,dtype=np.bool)
	cols_active = np.zeros(num_cols,dtype=np.bool)
	row_order = calc_group_order(row_constraints)
	col_order = calc_group_order(col_constraints)

	assert len(row_order) == len(row_constraints)
	assert len(col_order) == len(col_constraints)

	for index,row_data in enumerate(row_constraints):
		if all( item==0 for item in row_data):
			rows_active[index]=True

	for index,col_data in enumerate(col_constraints):
		if all( item==0 for item in col_data):
			cols_active[index]=True

	row_order = [ row_index for row_index in row_order if not rows_active[row_index]]
	col_order = [ col_index for col_index in col_order if not cols_active[row_index]]

	solver_row_helper(
		table=np.zeros([num_rows,num_cols],dtype=np.bool),
		row_size=row_size,
		col_size=col_size,
		row_order=row_order,
		col_order=col_order,
		rows_active=rows_active,
		cols_active=cols_active,
		row_data_list=row_constraints,
		col_data_list=col_constraints,
		index=0,
		table_checker_callback=table_checker_callback,
	)


def solver_row_helper(
	table,
	row_size,
	col_size,
	row_order,
	col_order,
	rows_active,
	cols_active,
	row_data_list,
	col_data_list,
	index,
	table_checker_callback,
):
	if index < len(row_order):
		row_index = row_order[index]
		for row in generate_valid_cell_group(row_data_list[row_index],row_size):
			if np.all(table[row_index,cols_active] == row[cols_active]):
				
				table[row_index,~cols_active]=row[~cols_active]
				rows_active[row_index] = True

				# print_table(table,"temp_output.txt",verbose=False)

				if index < len(cols_active):
					solver_col_helper(
						table,
						row_size,
						col_size,
						row_order,
						col_order,
						rows_active,
						cols_active,
						row_data_list,
						col_data_list,
						index,
						table_checker_callback,
					)

				else:
					table_checker_callback(table)

				table[row_index,~cols_active]=False
				rows_active[row_index] = False

	elif index < len(cols_active):
		solver_col_helper(
			table,
			row_size,
			col_size,
			row_order,
			col_order,
			rows_active,
			cols_active,
			row_data_list,
			col_data_list,
			index,
			table_checker_callback,
		)


def solver_col_helper(
	table,
	row_size,
	col_size,
	row_order,
	col_order,
	rows_active,
	cols_active,
	row_data_list,
	col_data_list,
	index,
	table_checker_callback,
):
	if index < len(col_order):
		col_index = col_order[index]
		for col in generate_valid_cell_group(col_data_list[col_index],col_size):
			if np.all(table[rows_active,col_index] == col[rows_active]):

				table[~rows_active,col_index]=col[~rows_active]
				cols_active[col_index]=True

				if index+1 < len(row_order):
					solver_row_helper(
						table,
						row_size,
						col_size,
						row_order,
						col_order,
						rows_active,
						cols_active,
						row_data_list,
						col_data_list,
						index+1,
						table_checker_callback,
					)

				else:
					table_checker_callback(table)

				table[~rows_active,col_index]=False
				cols_active[col_index]=False
	
	elif index+1 < len(row_order):
		solver_row_helper(
			table,
			row_size,
			col_size,
			row_order,
			col_order,
			rows_active,
			cols_active,
			row_data_list,
			col_data_list,
			index+1,
			table_checker_callback,
		)

