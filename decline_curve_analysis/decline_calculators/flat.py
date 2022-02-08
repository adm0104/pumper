import numpy as np
from .. import general_helpers as helpers

def calc_flat_forecast(time_vector, **kwargs):
    # Calculates harmonic decline rates and volumes, formatted for timeseries
    # dataframe in case.py
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array\
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    # OUTPUTS:
    #   gas_forecast            Full rate forecast as an array - 1st column
    #                           contains entry rates, 2nd column contains exit rates,
    #                           3rd column contains cumulative production volumes

    qi = kwargs['qi']
    rate_vector = calc_flat_rates(time_vector, qi)
    entry_rates, exit_rates = helpers.vector_to_endpoints(rate_vector)
    vols_vector = calc_flat_volumes(rate_vector)
    return np.array([entry_rates, exit_rates, vols_vector]).transpose()

def calc_flat_rates(time_vector, qi):
    # Calculates rates along time_vector per inputs qi and Di using Arps'
    # harmonic decline
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    # OUTPUTS:
    #   rate_vector             Vector of rates

    rate_vector = np.array([qi] * (time_vector.size))
    return rate_vector

def calc_flat_volumes(rate_vector):
    # Calculates volumes integral for harmonic decline between rates in 
    # rate_vector
    # INPUTS:
    #   rate_vector             Instantaneous rates for forecast, in numpy array
    #   Di                      Nominal initial decline rate
    # OUTPUTS:
    #   vols_vector             Vector of volumes

    c = helpers.read_settings()['days_in_month']
    vols_vector = rate_vector[:-1] * c
    return vols_vector