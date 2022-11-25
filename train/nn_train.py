# Copyright 2019 Siotic Spain, S.L.

import sys
import json
from sklearn.preprocessing import MinMaxScaler
from utils.dataset_utils import split_dataset_in_inputs_and_outputs, load_water_output_dataset_from, reframe_output_dataset_for_rnn
from nn_models.recurrent_model import *
from utils.results_analysis import plot_history, calculate_RMSE, build_tf_tensorboard_callbacks
from utils.logging_config import set_logging


# TODO: refactor this so there is a structure that holds each models related properties,
# and return a list of trained models using that structure
# The idea is to have a reference with all the useful information about the newly trained model(s)
# In that way, an external actor can decide whether to use the new models or not
def train(configfile_path, enable_visualization = False, enable_tensorboard = False):
    set_logging

    with open(configfile_path, "r") as confFile:
        inputs_configuration = json.loads(confFile.read())

    # load some parameters
    number_of_features_for_learning = inputs_configuration['number_of_features_for_learning']
    number_of_features_to_predict = inputs_configuration['number_of_features_to_predict']

    # this is location for generated models
    outputs_path = inputs_configuration['output_model_path']
    create_dir_if_needed(outputs_path)

    # load dataset
    input_dataset = load_water_output_dataset_from(inputs_configuration, enable_visualization)

    # scaling
    scaler = MinMaxScaler(feature_range=(0, 1))
    input_dataset_scaled = scaler.fit_transform(input_dataset)

    # frame as supervised learning
    reframed = reframe_output_dataset_for_rnn(inputs_configuration, input_dataset_scaled)

    # split into train and test sets
    values = reframed.values
    testing_offset = inputs_configuration['split_parameters']['testing_offset']
    train = values[:testing_offset, :]
    test = values[testing_offset:, :]

    # split both train and test in inputs and outputs
    train_X, train_y = split_dataset_in_inputs_and_outputs(inputs_configuration, train)
    test_X, test_y = split_dataset_in_inputs_and_outputs(inputs_configuration, test)

    # train the models
    history_list = []

    def training_fn(model, name, tensorboard=False):
        # fit network
        history = model.fit(
            train_X, train_y,
            epochs=75, batch_size=60, validation_data=(test_X, test_y),
            verbose=2, shuffle=False,
            callbacks=build_tf_tensorboard_callbacks() if enable_tensorboard else None
        )
        history_list.append((history, name))
        return model

    models = build_models(number_of_features_for_learning, inputs_configuration, training_fn, scaler)

    # plot error measurement for trained models
    if enable_visualization:
        for (history, name) in history_list:
            plot_history(history, name)

    models += load_models(inputs_configuration['models_to_load'])

    # print keras summary of each model architecture
    if enable_visualization:
        for model in models:
            print(model.summary())

    # calculate and print RMSE for each trained model
    for model in models:
        # make a prediction
        yhat = model.predict(test_X)

        # calculate RMSE
        rmse = calculate_RMSE(yhat, test_X, test_y, scaler, number_of_features_for_learning,
                              number_of_features_to_predict)
        print('Test RMSE: %.3f' % rmse) if enable_visualization else None

    return models

#if __name__== "__main__":
train("./conf/train_models_configuration.json", True, False)
