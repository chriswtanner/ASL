# ASL
The SignBank Project

# Authors:
- Thomas Fouts (University of Michigan)
- Ali Hindy (Stanford)
- Chris Tanner (Harvard)

# To Run Models:
> python3 ASL.py

The program accepts a few hyperparameters:

--model_type (one of {LSTM, BILSTM, CNN, BILSTMCNN})

--epochs (# of epochs)

--hidden_size (# of units in the 1st hidden layer)

--ensemble (True or False)

Our best performing model yielded 95.9 accuracy and can be run via:

> python3 ASL.py -m BILISTMCNN -e 75 -hs 768 -e True

# Repository Structure
- All data is in the "data" folder. To generate new data, run the Arduino Script "DataCollector.ino"
- All models are in the "src" folder. 
- To view the schematics in order to build one of our sensors yourself, view the "schematics" folder. 
