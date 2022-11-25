# File to perform prediction from trained model.h5
# Copyright 2019 Siotic Spain, S.L.
from threading import Thread
import json
import sys
import pandas as pd
import numpy as np
from utils.logging_config import set_logging
from utils.dataset_utils import load_scaler_from, load_water_output_dataset_from, reframe_output_dataset_for_rnn, split_dataset_in_inputs_and_outputs
from keras.models import load_model
from flask import Flask, request

def load_dataset(inputs_configuration, additional_values):
    # load parameters
    number_of_timesteps = inputs_configuration['number_of_timesteps']

    # load dataset
    input_dataset = load_water_output_dataset_from(inputs_configuration)

    # add new values
    listOfSeriesToAdd = [pd.Series(additional_values, index=input_dataset.columns)]
    return input_dataset.append(listOfSeriesToAdd, ignore_index=True)


def prepare_prediction_dataset(inputs_configuration, input_dataset_scaled):
    # load parameters
    number_of_timesteps = inputs_configuration['number_of_timesteps']

    # frame as supervised learning
    reframed = reframe_output_dataset_for_rnn(inputs_configuration, input_dataset_scaled)

    # take only last N data points (N > number_of_timesteps)
    values = reframed.values
    size_of_selected_dataset = number_of_timesteps + 25
    selected_dataset = values[-size_of_selected_dataset:, :]

    # return selected dataset as inputs ready to be used for prediction
    data_X, data_y = split_dataset_in_inputs_and_outputs(inputs_configuration, selected_dataset)
    return data_X


class WaterOutputPredictor:

    def __init__(self, configfile_path):
        set_logging

        with open(configfile_path, "r") as confFile:
            self.inputs_configuration = json.loads(confFile.read())

        # current model to load and use
        model_to_load = self.inputs_configuration['current_model']
        self.model = load_model(model_to_load)
        # TODO: make something more interesting with this ID...
        self.model_id = model_to_load

        # current scaler, same it was used to train the model
        self.scaler = load_scaler_from(self.inputs_configuration['scaler'])

    def describe_model(self):
        return {
            'model_id': self.model_id
        }

    def predict_for(self, values):
        # load needed parameters...
        number_of_features_for_learning = self.inputs_configuration['number_of_features_for_learning']
        number_of_features_to_predict = self.inputs_configuration['number_of_features_to_predict']

        # load values, adding the new ones
        input_dataset = load_dataset(self.inputs_configuration, values)

        # scaling
        input_dataset_scaled = self.scaler.fit_transform(input_dataset)

        # current dataset por prediction
        prediction_data = prepare_prediction_dataset(self.inputs_configuration, input_dataset_scaled)

        # we use the model to predict with this data now
        self.model._make_predict_function()
        scaled_prediction = self.model.predict(prediction_data)

        # replace in the dataset the labelled values with the prediction
        scaled_dataset = input_dataset_scaled[-scaled_prediction.shape[0]:, :]
        full_scaled_prediction = np.insert(
            scaled_dataset[:, number_of_features_to_predict:scaled_dataset.shape[1]],
            0,
            values = scaled_prediction.reshape(1, scaled_prediction.shape[0]),
            axis = 1)

        # invert the scaling...
        unscaled_prediction = self.scaler.inverse_transform(full_scaled_prediction)

        # the prediction is of course the last data point, returned as an array of output variables
        # TODO: refactor, maybe it is better to use a map instead of a list as basic datatype for both inputs and outputs? Like Pandas does...
        return unscaled_prediction[unscaled_prediction.shape[0]-1, :][0:number_of_features_to_predict]


#if __name__== "__main__":#
#    if (len(sys.argv)) != 5:
#        print('Wrong number of arguments: nn_make_prediction path_to_model_configuration water_precipitation water_height water_flow')
#    else:
#        predictor = WaterOutputPredictor(sys.argv[1])
#        result = predictor.predict_for([float(item) for item in sys.argv[2:5]])
#        print('Our prediction for water_flow for next day is: ' + str(result))
#else:


def make_prediction(arg0, arg1,arg3):
    predictor = WaterOutputPredictor('./conf/current_model_configuration.json')
    parameters = [arg0, arg1, arg3]
    calculated_values = predictor.predict_for(parameters)
    return (calculated_values[0] )
    
  

#print(make_prediction(sys.argv[1], sys.argv[2], sys.argv[3]))
#predictor.predict_for([1.53, 10.2, 31.12])
