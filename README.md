# ASL
The SignBank Project

# Authors:
- Thomas Fouts (Brunswick School)
- Ali Hindy (Brunswick School)
- Julia Kreutzer (Google Research)
- Chris Tanner (Harvard)

# To Run:
> python3 ASL.py

The program accepts a few hyperparameters:
--model_type (one of {LSTM, BILSTM, CNN, BILSTMCNN})
--epochs (# of epochs)
--hidden_size (# of units in the 1st hidden layer)
--ensemble (True or False)

Our best performing model yielded 95.9 accuracy and can be run via:

> python3 ASL.py -m BILISTMCNN -e 75 -hs 768 -e True


