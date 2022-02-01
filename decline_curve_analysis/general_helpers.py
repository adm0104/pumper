import pandas as pd
import numpy as np
import json

def read_settings():
    # Reads settings json file (settings.json)
    # Settings contains unit conversion constants, other user preferences
    # INPUTS:
    #   None
    # OUTPUTS:
    #   settings                Dictionary of user settings

    with open('settings.json') as f:
        return json.load(f)

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