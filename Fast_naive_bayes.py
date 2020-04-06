import time
import jieba
import pdb
import pandas as pd
from tqdm import tqdm
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
	return real_total_dict, fake_total_dict

real_df = pd.read_csv('1.csv')
real_messages = real_df['message']
real_labels = np.ones(len(real_messages)).tolist()

fake_df = pd.read_csv('0.csv')
fake_messages = fake_df['message']
fake_labels = np.zeros(len(fake_messages)).tolist()

'combine these data'
X = real_messages.copy().append(fake_messages)
real_labels.extend(fake_labels)
Y = real_labels
assert len(X) == len(Y)
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=42)
pdb.set_trace()
