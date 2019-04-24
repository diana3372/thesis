import sys
import os
import numpy as np
import pandas as pd

from enum import Enum

from stats_calculator import get_test_messages_stats, get_test_metrics, plot_training_meters_curves

debugging = False

class Mode(Enum):
	NORMAL = 0,
	AVG = 1

if len(sys.argv) == 1:
	# This is going to be broken....
	#all_folders_names = os.listdir('../dumps')
	#inputs = ['{} {}'.format(folder_name, folder_name[folder_name.find('_')+1:folder_name.rfind('_')]) for folder_name in all_folders_names]
	print('Usage python analyze.py [analysis_id] [data_folder] [mode=normal/average] [model_id1 V L lambda alpha] [model_id2 V L lambda alpha] ...')
	assert False
else:
	analysis_id = sys.argv[1]
	data_folder = sys.argv[2]
	mode = sys.argv[3]
	inputs = sys.argv[4:]

if 'v' in mode:
	mode = Mode.AVG
else:
	mode = Mode.NORMAL

if debugging:
	print("===========DEBUGGING==============")

plots_dir = 'plots' # individual
stats_dir = 'tables' # across experiments

if not os.path.exists(plots_dir):
	os.mkdir(plots_dir)

if not os.path.exists(stats_dir):
	os.mkdir(stats_dir)

stats_dict = {
	'dataset' : [],
	'id' : [],
	'|V|' : [],
	'L' : [],
	'Lambda' : [],
	'Alpha' : [],
	'Accuracy' : [],
	'Min message length' : [],
	'Max message length' : [],
	'Avg message length' : [],
	'N tokens used' : [],
	'Entropy' : [],
	'Perplexity' : [],
	'Message distinctness' : [],
	'RSA Sender-Receiver' : [],
	'RSA Sender-Input' : [],
	'RSA Receiver-Input' : [],
	'Topological similarity': []
}

# Read in the settings we want to analyze
for inp in inputs:
	model_id, vocab_size, L, vl_loss_weight, bound_weight = inp.split()

	if not debugging:
		min_len, max_len, avg_len, n_utt = get_test_messages_stats(model_id, vocab_size, data_folder, plots_dir, should_plot=False)
		acc, entropy, distinctness, rsa_sr, rsa_si, rsa_ri, topological_sim = get_test_metrics(model_id)
	else:
		model_id = 'debug_mode'
		acc = np.random.random()
		entropy = np.random.random()
		distinctness = np.random.random()
		rsa_sr = np.random.random()
		rsa_si = np.random.random()
		rsa_ri = np.random.random()
		topological_sim = np.random.random()
		min_len = np.random.randint(1,10)
		max_len = min_len + np.random.randint(2,5)
		avg_len = (min_len + max_len) / 2
		n_utt = np.random.randint(1, vocab_size)

	stats_dict['dataset'].append(data_folder)
	stats_dict['id'].append(model_id)
	stats_dict['|V|'].append(vocab_size)
	stats_dict['L'].append(L)
	stats_dict['Lambda'].append(vl_loss_weight)
	stats_dict['Alpha'].append(bound_weight)
	stats_dict['Accuracy'].append(acc)
	stats_dict['Min message length'].append(min_len)
	stats_dict['Max message length'].append(max_len)
	stats_dict['Avg message length'].append(avg_len)
	stats_dict['N tokens used'].append(n_utt)
	stats_dict['Entropy'].append(entropy)
	stats_dict['Perplexity'].append(np.exp(entropy))
	stats_dict['Message distinctness'].append(distinctness)
	stats_dict['RSA Sender-Receiver'].append(rsa_sr)
	stats_dict['RSA Sender-Input'].append(rsa_si)
	stats_dict['RSA Receiver-Input'].append(rsa_ri)
	stats_dict['Topological similarity'].append(topological_sim)

	print('id: {}, |V|: {}, L: {}, Lambda: {}, Alpha: {}, Accuracy: {}'.format(
		model_id, vocab_size, L, vl_loss_weight, bound_weight, acc))

# Dump all stats
df = pd.DataFrame(stats_dict)
df.to_csv('{}/{}_all_stats_{}.csv'.format(stats_dir, analysis_id, data_folder), index=None, header=True)

if mode == Mode.AVG:
	avg_stats_dict = {k: [] for k in stats_dict.keys() if k != 'id'}

	assert (all(d == stats_dict['dataset'][0] for d in stats_dict['dataset']) 
		and all(v == stats_dict['|V|'][0] for v in stats_dict['|V|']) 
		and all(l == stats_dict['L'][0] for l in stats_dict['L'])
		and all(l == stats_dict['Lambda'][0] for l in stats_dict['Lambda'])
		and all(a == stats_dict['Alpha'][0] for a in stats_dict['Alpha']))

	avg_stats_dict['dataset'].append(stats_dict['dataset'][0])
	avg_stats_dict['|V|'].append(stats_dict['|V|'][0])
	avg_stats_dict['L'].append(stats_dict['L'][0])
	avg_stats_dict['Lambda'].append(stats_dict['Lambda'][0])
	avg_stats_dict['Alpha'].append(stats_dict['Alpha'][0])

	for measure in list(avg_stats_dict.keys())[5:]:
		avg = sum([stats_dict[measure][idx] for idx in range(len(inputs))]) / len(inputs)
		avg_stats_dict[measure].append(avg)

	print('=Average for all models=\n|V|: {}, L: {}, Lambda: {}, Alpha: {}, Accuracy: {}'.format(
		avg_stats_dict['|V|'][0], 
		avg_stats_dict['L'][0], 
		avg_stats_dict['Alpha'][0], 
		avg_stats_dict['Lambda'][0], 
		avg_stats_dict['Accuracy'][0]))

	# Dump avg stats
	df = pd.DataFrame(avg_stats_dict)
	df.to_csv('{}/{}_avg_stats_{}.csv'.format(stats_dir, analysis_id, data_folder), index=None, header=True)

	plot_training_meters_curves(stats_dict['id'], '{}_{}'.format(analysis_id, data_folder), plots_dir)





# unique_VLs = {}
# for idx, (v, l) in enumerate(zip(stats_dict['|V|'], stats_dict['L'])):
# 	if (v,l) not in unique_VLs:
# 		unique_VLs[(v,l)] = [idx]
# 	else:
# 		unique_VLs[(v,l)].append(idx)

# avg_stats_dict = {k: [] for k in stats_dict.keys() if k != 'id'}

# for (v,l), idxs in unique_VLs.items():
# 	avg_stats_dict['|V|'].append(v)
# 	avg_stats_dict['L'].append(l)

# 	for measure in list(avg_stats_dict.keys())[2:]:
# 		acc = sum([stats_dict[measure][idx] for idx in idxs]) / len(idxs)
# 		avg_stats_dict[measure].append(acc)


# plot_acc_per_setting(avg_stats_dict, stats_dir, data_folder)