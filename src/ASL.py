from DataHandler import DataHandler
from Modeller import Modeller

import sys
import pickle
import random
import keras
import argparse

# allows for passing in a boolean (for "--ensemble")
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# handles passed-in arguments
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model_type", type=str, default="CNN", help ="{LSTM, BILSTM, CNN, BILSTMCNN}")
parser.add_argument("-e", "--epochs", default=5, type=int, help="# of epochs")
parser.add_argument("-hs", "--hidden_size", default=768, type=int, help ="# units in the 1st hidden layer")
parser.add_argument("-ens", "--ensemble", type=str2bool, default=False, help ="True or False")
args = parser.parse_args()

model_type = args.model_type
num_epochs = args.epochs
num_hidden_units = args.hidden_size
training_sets = [([1,2,3,4], [5])]

if args.ensemble:
    for i in reversed(range(1,5)):
        train = [1,2,3,4,5]
        train.remove(i)
        dev = [i]
        training_sets.append((train, dev))

# settings for converting sensor data
min_time_steps = 15
max_time_steps = 70

data_dir = "../data/"
sensors_file =  "558_signs.txt" #"80_signs.txt" #"558_signs.txt" # # # 
sensor_pickle_to_load = "558_signs_15_70.pickle" # "80_signs_15_70.pickle" #"558_signs_15_70.pickle"

# experiment hyperparameters
load_pickle = True
save_pickle = False

test_signs = [6,7] # ALWAYS (don't touch)
##########################################

# initializes a Modeller
m = Modeller(data_dir)

# loads data
dh = DataHandler(data_dir)
if load_pickle:
    sensor_data = pickle.load(open(data_dir + sensor_pickle_to_load, "rb"))
else:
    sensor_data = dh.load_sensors_file(sensors_file, min_time_steps, max_time_steps, save_pickle)

uid = model_type + "_epochs" + str(num_epochs) + "_h" + str(num_hidden_units)

# output metadata for models 
print("UID:", uid)
print("\tmodel_type:", model_type)
print("\tnum_epochs:", num_epochs)
print("\tnum_hidden_units:", num_hidden_units)
print("keras.__version__:", keras.__version__)

# makes the train/dev/test splits
sum_preds = []
for train_signs, dev_signs in training_sets:
    print("ts:", train_signs, "ds:", dev_signs)

    dev_preds, dev_golds, test_preds, test_golds = m.run_model(uid, model_type, dh, num_epochs, num_hidden_units, sensor_data, train_signs, dev_signs, test_signs)

    if len(sum_preds) == 0:
        sum_preds = test_preds
    else:
        for i, p in enumerate(test_preds):
            sum_preds[i] = [sum(x) for x in zip(p, sum_preds[i])]

    m.evaluate("DEVSET", dev_preds, dev_golds, sensor_data)
    m.evaluate("TESTSET", test_preds, test_golds, sensor_data)
    print("test_preds:", len(test_preds[0]))
m.evaluate("ENSEMBLE TESTSET", sum_preds, test_golds, sensor_data)
