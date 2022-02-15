import json
import importlib.resources
import pandas as pd
import numpy as np

def read_settings():
    # Reads settings json file (settings.json)
    # Settings contains unit conversion constants, other user preferences
    # INPUTS:
    #   None
    # OUTPUTS:
    #   settings                Dictionary of user settings

    with importlib.resources.open_text('pumper.helper_functions', 'settings.json') as file:
        return json.load(file)


def vector_to_endpoints(vector):
    # Function for assisting with endpoint definition in timeseries calculations
    # Converts a single numpy vector of size N into two arrays of size N - 1
    # "entry_vector" starts with value 0, ends with value N-1
    # 
    # INPUTS:
    #   vector                  Any N x 1 numpy array
    # OUTPUTS:
    #   entry_vector            numpy array including all elements of "vector" except last
    #   exit_vector             numpy array including all elements of "vector" except first

    entry_vector = vector[:-1]
    exit_vector = vector[1:]

    return entry_vector, exit_vector

def read_default_pricing():
    # Pulls pricing table from price file under scenario "default"
    # INPUTS:
    #   None
    # OUTPUTS:
    #   pricing                 Price table for econ run, formatted as json

    with importlib.resources.open_text('pumper.helper_functions', 'pricing.json') as file:
        price_json = json.load(file)

    return price_json