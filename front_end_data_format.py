

def build_year_month_slot_dict(res):
	year_month_slot = {}
	for single in res:
		year_month_val = '-'.join(single['_id']['date_val'].split('-')[:2])
		if year_month_val not in year_month_slot:
			year_month_slot[year_month_val] = []
		year_month_slot[year_month_val].append(single)
	return year_month_slot

def extract_suitable_timeline(current_slot):
	current_level_res = {}
	date_x_axis = []
	for current_single_slot in current_slot:
		room_id_val = current_single_slot['_id']['roomid']
		time_val = current_single_slot['_id']['date_val']
		'select independent date as x axis'
		if time_val not in date_x_axis:
			date_x_axis.append(time_val)
		if room_id_val not in current_level_res:
			current_level_res[room_id_val] = []
		'Push different messages according to the roomid'
		current_level_res[room_id_val].append(current_single_slot)
	'Make sure the date begin with lower part. needs check'
	date_x_axis.reverse()
	return current_level_res, date_x_axis

def month_level_format_change(current_room_res, date_x_axis):
	low_level_dict = {}
	for single_room in reversed(current_room_res):
		current_date = single_room['_id']['date_val']
		current_count = single_room['count']
		assert current_date not in low_level_dict, "logic error"
		low_level_dict[current_date] = current_count
	low_level_fin_data = []
	for single_date in date_x_axis:
		if single_date in low_level_dict:
			'If exist, then add count to the data'
			low_level_fin_data.append(low_level_dict[single_date])
		else:
			low_level_fin_data.append('')
	return low_level_fin_data


def build_front_end_data_format(name, data):
	return {
		'name': name,
		'type': 'bar',
		'stack': '总量',
		'data': data
	}