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

def slice_time_vector(start, stop, time_vector):
    # Returns a vector smaller or equal to time_vector in size, that
    # includes a number of months equal to stop - start. If neither
    # are defined, simply returns time_vector with define start and stop
    # at the beginning and end of time_vector
    # INPUTS:
    #   start                   Start month as string
    #   stop                    Stop month as string
    #                           Valid formatting for start and stop are:
    #                           "MM/YYYY", "MM-YYYY", "YYYY-MM", "YYYY/MM"
    #   time_vector             Vector of days in each month
    # OUTPUTS:
    #   start                   Start month as pd.Period object
    #   stop                    Stop month as pd.Period object
    #   time_vector_slice       Slice of time_vector from start to stop (inclusive)

    settings = read_settings()

    if start is None and stop is None:
        start = pd.Period(settings['effective_date'], 'M')
        stop = start + settings['forecast_duration']
        return start, stop, time_vector
    else:
        if start is None:
            start = settings['effective_date']
        else:
            start = pd.Period(start, 'M')

        if stop is None:
            stop = start + settings['forecast_duration']
        else:
            stop = pd.Period(stop, 'M')

        interval = (stop - start).n + 2
        return start, stop, time_vector[:interval]