import time
import pdb
import pandas as pd
from tqdm import tqdm
import numpy as np

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
			res_prob *= lowest_prob
	return res_prob

def predict_message(real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, real_lowest_prob, fake_lowest_prob, message):
	'naive bayes classifier'
	real_prob = prob_calculation(prior_of_real, real_total_dict, real_lowest_prob, message)
	fake_prob = prob_calculation(prior_of_fake, fake_total_dict, fake_lowest_prob, message)
	'then, we normalize these probabilities'
	real_prob /= real_prob + fake_prob
	fake_prob /= real_prob + fake_prob
	return real_prob, fake_prob

real_df = pd.read_csv('1.csv')
real_messages = shuffle_dataframe(real_df['message'])

fake_df = pd.read_csv('0.csv')
fake_messages = shuffle_dataframe(fake_df['message'])

'split train test sets'
train_ratio = 0.8
train_real_messages = real_messages[:int(len(real_messages) * train_ratio)]
train_fake_messages = fake_messages[:int(len(fake_messages) * train_ratio)]

test_real_messages = real_messages[int(len(real_messages) * train_ratio):]
test_fake_messages = fake_messages[int(len(fake_messages) * train_ratio):]

real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, real_lowest_prob, fake_lowest_prob = train_naive_bayes(train_real_messages, train_fake_messages)

'Merge test cases'
total_test_messages = test_real_messages.copy().append(test_fake_messages)
total_test_labels = [1 for _ in test_real_messages] + [0 for _ in test_fake_messages]

for (label, single_test_messages) in zip(total_test_labels, total_test_messages):
	real_prob, fake_prob = predict_message(real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, real_lowest_prob, fake_lowest_prob, single_test_messages)
	pdb.set_trace()