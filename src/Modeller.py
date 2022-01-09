import operator
import numpy as np
from collections import defaultdict
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Bidirectional
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import Conv1D
from keras.layers import Flatten
from keras.layers import MaxPooling2D
from keras.layers import MaxPooling1D
from keras.layers import TimeDistributed
from keras.layers import BatchNormalization
class Modeller:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def run_model(self, uid, model_type, dh, num_epochs, num_hidden_units, sensor_data, train_signs, dev_signs, test_signs):
        
        # hyperparameters for constructing data
        max_length = 70
        num_features = 30
        num_classes = len(sensor_data.keys())
        padding_num = -300

        train_x, train_y = dh.construct_data(sensor_data, train_signs, max_length, padding_num)
        dev_x, dev_y = dh.construct_data(sensor_data, dev_signs, max_length, padding_num)
        test_x, test_y = dh.construct_data(sensor_data, test_signs, max_length, padding_num)

        #train_x.reshape(max_length, num_features)

        print("train_x shape:", train_x.shape, "train_y:", train_y.shape)
        print("dev_x shape:", dev_x.shape, "dev_x:", dev_y.shape)
        print("test_x shape:", test_x.shape, "test_x:", test_y.shape)

        optimizer = "adam" #"rmsprop"
        loss = "categorical_crossentropy"
        metrics = ["accuracy"]

        model = Sequential()

        if model_type == "LSTM":
            model.add(LSTM(num_hidden_units, input_shape=(max_length, num_features)))
            model.add(LSTM(512))
            
        elif model_type == "BILSTM":
            model.add(Bidirectional(LSTM(num_hidden_units, return_sequences=True, input_shape=(max_length, num_features))))
            model.add(BatchNormalization())
            model.add(Bidirectional(LSTM(512))) #return_sequences=True
        
        elif model_type == "BILSTM_BIG":
            model.add(Bidirectional(LSTM(num_hidden_units, return_sequences=True, input_shape=(max_length, num_features))))
            model.add(BatchNormalization())
            model.add(Bidirectional(LSTM(1024))) #return_sequences=True
        
        elif model_type == "CNN":
            model.add(Conv1D(64, (2), activation='relu', input_shape=(max_length, num_features)))
            model.add(BatchNormalization())
            model.add(MaxPooling1D())
            model.add(Dropout(0.4))
            model.add(Flatten())

        elif model_type == "BILSTMCNN":
            model.add(Bidirectional(LSTM(num_hidden_units, return_sequences=True, input_shape=(max_length, num_features))))
            model.add(BatchNormalization())
            model.add(Dropout(0.4))

            model.add(Conv1D(64, (4), activation='relu'))
            model.add(BatchNormalization())
            model.add(MaxPooling1D())
            model.add(Dropout(0.4))
            
            model.add(Conv1D(16, (2), activation='relu'))
            model.add(BatchNormalization())
            model.add(MaxPooling1D())
            model.add(Flatten())
        else:
            print("** ERROR: model type not implemented yet!")
            exit()

        model.add(Dense(num_classes, activation='softmax'))
        model.build((None, max_length, num_features))

        model.summary()

        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        model.fit(train_x, train_y, epochs=num_epochs, shuffle=True, verbose=1)

        # save model
        model.save(self.data_dir + uid + ".h5")

        # load model
        #model = load_model('lstm_model.h5')

        # make predictions
        dev_preds = model.predict(dev_x, verbose=1)
        test_preds = model.predict(test_x, verbose=1)
        
        dev_scores = model.evaluate(dev_x, dev_y, verbose=1)
        print("DEV Accuracy: %.2f%%" % (dev_scores[1]*100))

        test_scores = model.evaluate(test_x, test_y, verbose=1)
        print("TEST Accuracy: %.2f%%" % (test_scores[1]*100))

        return dev_preds, dev_y, test_preds, test_y

    def evaluate(self, data_set, preds, golds, sensor_data):

        index_to_word = {}
        word_to_err = {}
        for i, word in enumerate(sorted(sensor_data.keys())):
            index_to_word[i] = word

        correct = 0
        recall_levels = defaultdict(list)
        for row_num in range(len(preds)):
            
            # concerns @ 1 accuracy
            max_gold_index = np.argmax(golds[row_num])
            max_pred_index = np.argmax(preds[row_num])
            #print("max_gold_index:", max_gold_index, "max_pred_index:", max_pred_index)
            if max_gold_index == max_pred_index:
                correct += 1
            err = 1 - preds[row_num][max_gold_index]
            word_to_err[index_to_word[max_gold_index]] = err

            # concerns recall at various levels
            index_to_prob = {}
            for i in range(len(preds[row_num])):
                index_to_prob[i] = preds[row_num][i]
            
            found_gold = False
            for i, (k, v) in enumerate(sorted(index_to_prob.items(), key=operator.itemgetter(1), reverse=True)):
                if k == max_gold_index:
                    found_gold = True
                    
                if found_gold:
                    recall_levels[i+1].append(1)
                else:
                    recall_levels[i+1].append(0)
        acc = 100*float(correct) / len(golds)

        # prints the misses
        '''
        print("\n-------------------------\n** RESULTS FOR:", data_set, "\n-------------------------")
        for i, (k, v) in enumerate(sorted(word_to_err.items(), key=operator.itemgetter(1), reverse=True)):
            if i > 20:
                break
            print(i, k, v)
        '''

        recall_prints = [1, 5, 10, 25, 100]
        perfect_level = -1
        for i in range(1, len(recall_levels.keys())+1):
            found = recall_levels[i].count(1)
            recall = float(found) / len(recall_levels[i])
            if i in recall_prints:
                print(data_set, "RECALL @", i, ":", recall)
            if perfect_level == -1 and recall == 1:
                perfect_level = i
        print(data_set, "Perfect RECALL @", perfect_level)
        print(data_set, "ACC:", acc)
