import re
import sys
import pickle
import numpy as np
from numpy import array
from collections import defaultdict
from keras.utils import to_categorical
from keras.preprocessing import sequence
import tensorflow as tf

import matplotlib.pyplot as plt
from matplotlib import colors
# loads and processes the input/output data
class DataHandler:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.sensors_all = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
    # constructs X, Y data for the passed_in signing numbers (e.g., [6,7])
    def construct_data(self, sensor_data, sign_numbers, max_length, padding_num):
        #max_v = -9
        #min_v = 9

        # word to index (dictionary for the O(1) lookup)
        word_to_index = {} 
        for i, cur_word in enumerate(sorted(sensor_data.keys())):
            word_to_index[cur_word] = i
        
        X = []
        Y = []
        for cur_word in sensor_data.keys():
            
            for sign_num in sign_numbers:
                sign_data = []
                for time_step in sensor_data[cur_word][sign_num]:
                    #max_v = max(max_v, np.max(sensor_data[cur_word][sign_num][time_step]))
                    #min_v = min(min_v, np.min(sensor_data[cur_word][sign_num][time_step]))
                    sign_data.append(sensor_data[cur_word][sign_num][time_step])
                    #print("sign_data:", sign_data)
            
                #print(cur_word, "a:", len(sign_data))
                #print(len(sign_data[0]))
                #break
                X.append(sign_data)
                Y.append(word_to_index[cur_word])
        X = sequence.pad_sequences(array(X), maxlen=max_length, padding='post', value=padding_num)
        tf.dtypes.cast(X, tf.float32)
        Y = to_categorical(Y)
        tf.dtypes.cast(Y, tf.float32)
        #Y = tf.cast(Y, dtype='float32')
        return X, Y
        
    # ensures both dictionaries have: (a) left and right hands; (b) 7 vectors each
    def validate_sign_data(self, word, emg_data, gyro_data):

        for hand in ["left", "right"]:
            if hand not in emg_data or hand not in gyro_data:
                sys.exit(str("** ERROR: we're missing a hand's worth of data for: " + word))
            
            if len(emg_data[hand]) != 7 or len(gyro_data[hand]) != 7:
                print("** IGNORING:", word, "because we don't have 7 signings for the", hand,"hand (skipping it)")
                return False
  
        # ensures the time series data is of the same size
        for sign_num in range(1,8):

            le = len(emg_data["left"][sign_num])
            re = len(emg_data["right"][sign_num])
            rg = len(gyro_data["left"][sign_num])
            lg = len(gyro_data["right"][sign_num])

            if le != re:
                sys.exit(str("** ERROR: amount of emg data differs across hands!"))
            if lg != rg:
                sys.exit(str("** ERROR: amount of gryo data differs across hands!"))
            if lg != 0 and lg > le + 1:
                print("** WARNING: gyro contains:", lg, "time recordings whereas emg only has", le)
        return True
    

    # example: sensors_all['above'][signing_number][time_step = [30]
    def add_word(self, timings, min_time_steps, max_time_steps, cur_word, emg_data, gyro_data):

        include_word = True
        for sign_num in range(1,8):
            
            # we clip the gyro data by constructing from the emg data's time length
            num_timings = len(emg_data["left"][sign_num])
            timings.append(num_timings) #[num_timings] += 1
            if num_timings < min_time_steps:
                include_word = False
                print("** IGNORING:", cur_word, "because it has a signage of timelength:", num_timings)
                break

            for time_step in range(min(num_timings, max_time_steps)):
                stacked = [emg_data["right"], emg_data["left"], gyro_data["right"], gyro_data["left"]]
                flat_vec = [j for v in stacked for j in v[sign_num][time_step]]
                self.sensors_all[cur_word][sign_num][time_step] = flat_vec

        if not include_word and cur_word in self.sensors_all:
            del self.sensors_all[cur_word] # the earlier signings could allow it to be added
        
    # loads the sensors file (e.g., 'combined.txt') and produces a nested dictionary:
    # sensors_all['above'][signing_number][time_step] = [30]
    def load_sensors_file(self, sensors_file, min_time_steps, max_time_steps, save_pickle):

        self.sensors_all = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        processed_words = set()
        with open(self.data_dir + sensors_file,'r') as fopen:
            cur_hand = ""
            cur_sign_number = -1
            cur_word = ""
            
            # stores ['left' or 'right'][sign_number] = list of lists
            emg_data = defaultdict(lambda: defaultdict(list))
            gyro_data = defaultdict(lambda: defaultdict(list))
            
            timings = [] #defaultdict(int)
            for line in fopen:
                line = line.strip(' ,\n').lower()
                
                # regex to extract info we want
                hand_matches = re.search(r"(\S+) \S+ data, word, (\S+)", line)
                sign_matches = re.search(r"sign number, (\d+)", line)
                emg_data_matches = re.search(r"^(\d+,){4}(\d+)$", line)
                gyro_data_matches = re.search(r"^(\S+,){9}(\S+)$", line)
                
                # parses each line for relevant info
                if hand_matches:
                    cur_hand = hand_matches.group(1)
                    cur_word = hand_matches.group(2)
                elif sign_matches:
                    cur_sign_number = int(sign_matches.group(1))
                elif emg_data_matches:
                    emg_data[cur_hand][cur_sign_number].append([float(x) for x in line.split(",")])
                elif gyro_data_matches:
                    gyro_data[cur_hand][cur_sign_number].append([float(x) for x in line.split(",")])
                elif line == "***thats 7 signs***":

                    # ignores duplicates in the original txt file
                    if cur_word not in processed_words:
                        
                        # ensures the data is valid
                        if self.validate_sign_data(cur_word, emg_data, gyro_data):
                            self.add_word(timings, min_time_steps, max_time_steps, cur_word, emg_data, gyro_data)

                    processed_words.add(cur_word)                    
                    emg_data = defaultdict(lambda: defaultdict(list))
                    gyro_data = defaultdict(lambda: defaultdict(list))
        
        print("sensors_all:", sorted(self.sensors_all.keys()))
        print("# words loaded:", len(self.sensors_all.keys()))
        
        # makes a histogram of the sensor recordings
        '''
        fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
        axs.hist(timings, bins=15, color="#91171F", alpha = 1)
        plt.title("Sensor recordings per individual signing",fontsize=20)
        plt.xlabel("Number of sensor recordings", fontsize=16)
        plt.ylabel("Count", fontsize=16)
        plt.show()
        '''

        # optionally saves our file to a pickle, for faster loading later
        # since defaultdict() isn't picklable, we need to reformat it as a native dictionary
        if save_pickle:
            l1 = {}
            for k1 in self.sensors_all:
                l2 = {}
                for k2 in self.sensors_all[k1]:
                    l3 = {}
                    for k3 in self.sensors_all[k1][k2]:
                        l3[k3] = self.sensors_all[k1][k2][k3]
                    l2[k2] = l3
                l1[k1] = l2

            fout = open(self.data_dir + sensors_file[0:sensors_file.index(".")] + "_" + str(min_time_steps) + "_" + str(max_time_steps) + ".pickle", "wb")
            pickle.dump(l1, fout)
            fout.close()
            
        return self.sensors_all