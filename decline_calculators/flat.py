import numpy as np
from .. import helper_functions as helpers

# flat.py is the core calculator for flat forecasts
#
# Flat forecasts do not represent a particular form of flow or drainage,
# but are useful when creating custom forecasts

def calc_flat_forecast(time_vector, **kwargs):
    # Calculates flat rates and volumes, formatted for timeseries
    # dataframe in case.py
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array\
    #   qi                      Initial rate, will not change
    # OUTPUTS:
    #   forecast                Full rate forecast as an array - 1st column
    #                           contains entry rates, 2nd column contains exit rates,
    #                           3rd column contains cumulative production volumes

    qi = kwargs['qi']
    rate_vector = calc_flat_rates(time_vector, qi)
    entry_rates, exit_rates = helpers.vector_to_endpoints(rate_vector)
    vols_vector = calc_flat_volumes(rate_vector)
    return np.array([entry_rates, exit_rates, vols_vector]).transpose()

def calc_flat_rates(time_vector, qi):
    # Generates rate_vector as an array populated with values equal to qi
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate, will not change
    # OUTPUTS:
    #   rate_vector             Vector of rates

    rate_vector = np.array([qi] * (time_vector.size))
    return rate_vector

def calc_flat_volumes(rate_vector):
    # Calculates volume per timestep at rate = qi
    # INPUTS:
    #   rate_vector             Instantaneous rates for forecast, in numpy array
    # OUTPUTS:
    #   vols_vector             Vector of volumes

    c = helpers.read_settings()['days_in_month']
    vols_vector = rate_vector[:-1] * c
    return vols_vector