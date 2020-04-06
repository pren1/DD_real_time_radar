import time
import jieba
import pdb
import pandas as pd
from tqdm import tqdm
import random
import numpy as np
from sklearn.model_selection import train_test_split
# seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
# print([x for x in seg_list])
# start_time = time.time()
# seg_list = jieba.cut("( ´_ゝ｀)", cut_all=False)
# print([x for x in seg_list])
# print("--- %s seconds ---" % (time.time() - start_time))

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
		# total_dict_length = sum(dict.values())
		dict = {k: v / total for total in (sum(dict.values()),) for k, v in dict.items()}
		if sort:
			return {k: v for k, v in sorted(dict.items(), key=lambda item: item[1])}
		else:
			return dict

	real_total_dict = train_empty_dict(total_dict.copy(), real_messages, sort=True)
	fake_total_dict = train_empty_dict(total_dict.copy(), fake_messages, sort=True)
	return real_total_dict, fake_total_dict, prior_of_real, prior_of_fake

def shuffle_dataframe(df):
	return df.sample(frac=1).reset_index(drop=True)

def prob_calculation(prior, prob_dict, message):
	'calculate the prob of one class'
	res_prob = prior
	for single_char in message:
		res_prob *= prob_dict[single_char]
	return res_prob

def predict_message(real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, message):
	'naive bayes classifier'
	real_prob = prob_calculation(prior_of_real, real_total_dict, message)
	fake_prob = prob_calculation(prior_of_fake, fake_total_dict, message)
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

real_total_dict, fake_total_dict, prior_of_real, prior_of_fake = train_naive_bayes(train_real_messages, train_fake_messages)

'Merge test cases'
total_test_messages = test_real_messages.copy().append(test_fake_messages)
total_test_labels = [1 for _ in test_real_messages] + [0 for _ in test_fake_messages]

for (label, single_test_messages) in zip(total_test_labels, total_test_messages):
	real_prob, fake_prob = predict_message(real_total_dict, fake_total_dict, prior_of_real, prior_of_fake, single_test_messages)
	pdb.set_trace()