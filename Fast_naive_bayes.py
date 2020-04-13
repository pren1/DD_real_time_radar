import time
import pdb
import pandas as pd
from tqdm import tqdm
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

def train_naive_bayes(real_messages, fake_messages):
	total_messages = real_messages.copy().append(fake_messages)
	'prior prob'
	prior_of_real = len(real_messages)/(len(total_messages))
	prior_of_fake = len(fake_messages)/(len(total_messages))
	'features. First, you got all the distinct words'
	total_dict = {}
	for single_message in tqdm(total_messages):
		for single in single_message:
			if single not in total_dict:
				total_dict[single] = 0

	'Then, train this by counting the number of each sets'
	def train_empty_dict(dict, messages, sort=False):
		for single_message in tqdm(messages):
			for single in single_message:
				dict[single] += 1
		'Let us apply the laplacian smoothing here'
		smoothed_lowest_prob = 1 / (sum(dict.values()) + 2)
		dict = {k: (v + 1) / (total + 2) for total in (sum(dict.values()),) for k, v in dict.items()}
		if sort:
			return {k: v for k, v in sorted(dict.items(), key=lambda item: item[1])}, smoothed_lowest_prob
		else:
			return dict, smoothed_lowest_prob

	real_total_dict, real_lowest_prob = train_empty_dict(total_dict.copy(), real_messages, sort=True)
	fake_total_dict, fake_lowest_prob = train_empty_dict(total_dict.copy(), fake_messages, sort=True)
	return real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, real_lowest_prob, fake_lowest_prob

def shuffle_dataframe(df):
	return df.sample(frac=1).reset_index(drop=True)

def prob_calculation(prior, prob_dict, lowest_prob, message):
	'calculate the prob of one class'
	res_prob = prior
	for single_char in message:
		if single_char in prob_dict:
			res_prob *= prob_dict[single_char]
		else:
			# print("This character outside")
			res_prob *= lowest_prob
	return res_prob

def predict_message(real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, real_lowest_prob, fake_lowest_prob, message):
	'naive bayes classifier'
	real_prob = prob_calculation(prior_of_real, real_total_dict, real_lowest_prob, message)
	fake_prob = prob_calculation(prior_of_fake, fake_total_dict, fake_lowest_prob, message)

	total_prob = real_prob + fake_prob
	'then, we normalize these probabilities'
	real_prob /= total_prob
	fake_prob /= total_prob
	return real_prob, fake_prob

def save_data_array_as_npy(input_array, file_name):
	np.save(file_name, input_array)

def load_data_array_from_npy(file_name):
	return np.load(file_name, allow_pickle=True).tolist()

class Naive_Bayes(object):
	def __init__(self):
		self.read_out_dict = load_data_array_from_npy('trained_naive_bayes.npy')

	def decide_class(self, single_test_messages):
		real_prob, fake_prob = predict_message(
			self.read_out_dict['real_total_dict'],
			self.read_out_dict['fake_total_dict'],
			self.read_out_dict['prior_of_real'],
			self.read_out_dict['prior_of_fake'],
			self.read_out_dict['real_lowest_prob'],
			self.read_out_dict['fake_lowest_prob'], single_test_messages)

		pred_label = bool(real_prob > fake_prob)
		return pred_label, f"Naive bayes labeled {single_test_messages} as {pred_label} with prob {max(real_prob, fake_prob)}"

if __name__ == '__main__':
	NB_classifier = Naive_Bayes()

	import time
	start_time = time.time()
	is_interpretation, log_meg = NB_classifier.decide_class('(-_-)|||')
	print("--- %s seconds ---" % (time.time() - start_time))
	pdb.set_trace()
	real_df = pd.read_csv('1.csv')
	real_messages = shuffle_dataframe(real_df['message'])

	fake_df = pd.read_csv('0.csv')
	fake_messages = shuffle_dataframe(fake_df['message'])

	'split train test sets'
	train_ratio = 0.80
	train_real_messages = real_messages[:int(len(real_messages) * train_ratio)]
	train_fake_messages = fake_messages[:int(len(fake_messages) * train_ratio)]

	test_real_messages = real_messages[int(len(real_messages) * train_ratio):]
	test_fake_messages = fake_messages[int(len(fake_messages) * train_ratio):]

	real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, real_lowest_prob, fake_lowest_prob = train_naive_bayes(train_real_messages, train_fake_messages)

	save_dict = {}
	save_dict['real_total_dict'] = real_total_dict
	save_dict['fake_total_dict'] = fake_total_dict
	save_dict['prior_of_real'] = prior_of_real
	save_dict['prior_of_fake'] = prior_of_fake
	save_dict['real_lowest_prob'] = real_lowest_prob
	save_dict['fake_lowest_prob'] = fake_lowest_prob

	save_data_array_as_npy(save_dict, 'trained_naive_bayes')
	read_out_dict = load_data_array_from_npy('trained_naive_bayes.npy')
	# read_out_dict = save_dict
	# pdb.set_trace()
	'Merge test cases'
	total_test_messages = test_real_messages.copy().append(test_fake_messages)
	total_test_labels = [1 for _ in test_real_messages] + [0 for _ in test_fake_messages]

	correct_label_counter = []
	pred_results = []
	for (label, single_test_messages) in tqdm(zip(total_test_labels, total_test_messages)):
		real_prob, fake_prob = predict_message(
			read_out_dict['real_total_dict'],
			read_out_dict['fake_total_dict'],
			read_out_dict['prior_of_real'],
			read_out_dict['prior_of_fake'],
			read_out_dict['real_lowest_prob'],
			read_out_dict['fake_lowest_prob'], single_test_messages)
		pred_label = int(real_prob > fake_prob)
		pred_results.append(pred_label)
		correct_label_counter.append(int(pred_label == label))
		if not pred_label == label:
			print(f"{single_test_messages}: {label}")
	print(f"So, naive bayes accuracy could be: {np.sum(correct_label_counter)/len(total_test_labels)}")
	'draw metrices'
	print(confusion_matrix(total_test_labels, pred_results))
	print(classification_report(total_test_labels, pred_results))