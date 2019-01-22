import sys


def add_element_to_set(cur_set, element):
	if (len(cur_set | set([element])) > len(cur_set)):
		cur_set.add(element)
		return True
	return False


def add_list_of_elements_to_set(cur_set, list_of_elements):
	tmp_set = cur_set | set(list_of_elements)
	if (len(tmp_set) > len(cur_set)):
		cur_set |= tmp_set
		return True
	return False


def error_handler(type_of_error, error_massage):
	# int("x")
	print(type_of_error, error_massage)
	sys.exit()
