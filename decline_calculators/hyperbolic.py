import numpy as np
from .. import helper_functions as helpers
from . import harmonic as har

# hyperbolic.py is the core calculator for Arps' hyperbolic decline
#
# Hyperbolic deline is appropriate for reservoirs experiencing either
# transient flow (b > 1) or volumetric drainage
#
# b = 1 is a "divides by zero" edge case, and requires a harmonic solution
# If b = 1, these functions will instead pass their inputs to their
# harmonic counterparts in "harmonic.py"

def calc_hyperbolic_forecast(time_vector, **kwargs):
    # Calculates hyperbolic decline rates and volumes, formatted for timeseries
    # dataframe in case.py
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    # OUTPUTS:
    #   forecast                Full rate forecast as an array - 1st column
    #                           contains entry rates, 2nd column contains exit rates,
    #                           3rd column contains cumulative production volumes

    qi, Di, b = kwargs['qi'], kwargs['Di'], kwargs['b']

    if b != 1:
        rate_vector = calc_hyperbolic_rates(time_vector, qi, Di, b)
        entry_rates, exit_rates = helpers.vector_to_endpoints(rate_vector)
        vols_vector = calc_hyperbolic_volumes(time_vector, rate_vector, Di, b)
        return np.array([entry_rates, exit_rates, vols_vector]).transpose()
    else:
        return har.calc_harmonic_forecast(time_vector, qi, Di)
    

def calc_hyperbolic_rates(time_vector, qi, Di, b):
    # Calculates rates along time_vector per inputs qi and Di using Arps'
    # hyperbolic decline
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    # OUTPUTS:
    #   rate_vector             Vector of rates

    if b != 1:
        c = helpers.read_settings()['days_in_year']
        rate_vector = qi / (1 + b * Di * time_vector / c) ** (1 / b)
        return rate_vector
    else:
        return har.calc_harmonic_rates(time_vector, qi, Di)

def calc_hyperbolic_volumes(time_vector, rate_vector, Di, b):
    # Calculates volumes integral for hyperbolic decline between rates in 
    # rate_vector
    # INPUTS:
    #   rate_vector             Instantaneous rates for forecast, in numpy array
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    # OUTPUTS:
    #   vols_vector             Vector of volumes

    if b != 1:
        c = helpers.read_settings()['days_in_year']
        Di_moving = Di / (1 + b * Di * time_vector[:-1] / c)
        vols_vector = ((rate_vector[:-1] ** b) / ((1 - b) * Di_moving)) * (rate_vector[:-1] ** (1 - b) - rate_vector[1:] ** (1 - b)) * c
        return vols_vector
    else:
        return har.calc_harmonic_volumes(time_vector, rate_vector, Di)