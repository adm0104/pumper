import numpy as np
from .. import helper_functions as helpers

# exponential.py is the core calculator for Arps' exponential decline
#
# Exponential decline is appropriate for reservoirs experiencing volumetric drainage
# Will generate a straight-line forecast on a semilog plot of rate vs time (y = log, x = cartesian)

def calc_exponential_forecast(time_vector, **kwargs):
    # Calculates exponential decline rates and volumes, formatted for timeseries
    # dataframe in case.py
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    # OUTPUTS:
    #   forecast                Full rate forecast as an array - 1st column contains
    #                           entry rates, 2nd column contains exit rates,
    #                           3rd column contains cumulative production volumes

    qi, Di = kwargs['qi'], kwargs['Di']
    rate_vector = calc_exponential_rates(time_vector, qi, Di)
    entry_rates, exit_rates = helpers.vector_to_endpoints(rate_vector)
    vols_vector = calc_exponential_volumes(rate_vector, Di)
    return np.array([entry_rates, exit_rates, vols_vector]).transpose()

def calc_exponential_rates(time_vector, qi, Di):
    # Calculates rates along time_vector per inputs qi and Di using Arps' exponential
    # decline
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    # OUTPUTS:
    #   rate_vector             Vector of rates

    c = helpers.read_settings()['days_in_year']
    rate_vector = qi * np.exp(-Di * time_vector * (1 / c))
    return rate_vector

def calc_exponential_volumes(rate_vector, Di):
    # Calculates volumes integral for exponential decline between rates in 
    # rate_vector
    # INPUTS:
    #   rate_vector             Instantaneous rates for forecast, in numpy array
    #   Di                      Nominal initial decline rate
    # OUTPUTS:
    #   vols_vector             Vector of volumes

    c = helpers.read_settings()['days_in_year']
    vols_vector = (rate_vector[:-1] - rate_vector[1:]) * c / Di
    return vols_vector