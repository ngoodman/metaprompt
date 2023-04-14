
#load data from pickle
import pickle
with open('eval_data_gpt4_e1_r7.pkl', 'rb') as f:
    data = pickle.load(f)

#compute stats for user turns over all tests, across episodes
# data is a list of tests, each test is a list of dicts, each dict is an episode
# each episode dict has a key 'user_turns' which is an int
# so we want to extract the user_turns from each episode number, 
# and then compute the mean and std over a given episode number
import numpy as np
#extract user turns from each episode
user_turns = [[d['turns'] for d in test] for test in data]
#compute mean of nth episode across all tests
num_tests = len(user_turns[0])
episode_means = [np.mean([test[i] for test in user_turns]) for i in range(num_tests)]
#compute std of nth episode across all tests
episode_stds = [np.std([test[i] for test in user_turns]) for i in range(num_tests)]

#plot
import matplotlib.pyplot as plt
plt.errorbar(range(num_tests), episode_means, yerr=episode_stds)
plt.xlabel("episode number")
plt.ylabel("mean user turns")
#save plot
plt.savefig("eval_gpt4_e1_r7.png")