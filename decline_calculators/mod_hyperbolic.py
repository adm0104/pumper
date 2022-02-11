import numpy as np
from . import exponential as exp, hyperbolic as hyp
from .. import helper_functions as helpers

def calc_mod_hyperbolic_forecast(time_vector, **kwargs):
    # Calculates hyperbolic decline rates and volumes, formatted for timeseries
    # dataframe in case.py
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array\
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    # OUTPUTS:
    #   gas_forecast            Full rate forecast as an array - 1st column
    #                           contains entry rates, 2nd column contains exit rates,
    #                           3rd column contains cumulative production volumes

    qi, Di, b, Dt = kwargs['qi'], kwargs['Di'], kwargs['b'], kwargs['Dt']
    t_switch, q_switch = terminal_switch(qi, Di, b, Dt)

    rate_vector_hyperbolic = hyp.calc_hyperbolic_rates(time_vector[time_vector <= t_switch], qi, Di, b)
    rate_vector_exponential = exp.calc_exponential_rates(time_vector[time_vector > t_switch] - t_switch, q_switch, Dt)
    rate_vector = np.concatenate([rate_vector_hyperbolic, rate_vector_exponential])
    entry_rates, exit_rates = helpers.vector_to_endpoints(rate_vector)

    vols_vector = calc_mod_hyperbolic_volumes(time_vector[time_vector <= t_switch], rate_vector_hyperbolic, rate_vector_exponential, Di, Dt, b)

    return np.array([entry_rates, exit_rates, vols_vector]).transpose()

def calc_mod_hyperbolic_rates(time_vector, qi, Di, Dt, b, t_switch, q_switch):
    # Calculates rates along time_vector per inputs qi and Di using Arps'
    # hyperbolic decline
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    # OUTPUTS:
    #   rate_vector             Vector of rates

    rate_vector_hyperbolic = hyp.calc_hyperbolic_rates(time_vector[time_vector <= t_switch], qi, Di, b)
    rate_vector_exponential = exp.calc_exponential_rates(time_vector[time_vector > t_switch] - t_switch, q_switch, Dt)
    return np.concatenate([rate_vector_hyperbolic, rate_vector_exponential])

def calc_mod_hyperbolic_volumes(time_vector, rate_vector_hyperbolic, rate_vector_exponential, Di, Dt, b):
    # Calculates volumes integral for hyperbolic decline between rates in 
    # rate_vector
    # INPUTS:
    #   rate_vector             Instantaneous rates for forecast, in numpy array
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    # OUTPUTS:
    #   vols_vector             Vector of volumes

    vols_vector_hyperbolic = hyp.calc_hyperbolic_volumes(time_vector, rate_vector_hyperbolic, Di, b)
    vol_switch = np.array([0])
    vols_vector_exponential = exp.calc_exponential_volumes(rate_vector_exponential, Dt)
    return np.concatenate([vols_vector_hyperbolic, vol_switch, vols_vector_exponential])

def calc_t_switch(Di, b, Dt):
    # Calculates point in time when the switch from hyperbolic to exponential decline occurs
    # Applicable only for modified hyperbolic declines
    # INPUTS:
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    #   Dt                      Terminal decline rate
    # OUTPUTS:
    #   t_switch                Time to switch from hyperbolic to exponential (years)

    c = helpers.read_settings()['days_in_year']
    return (Di / Dt - 1) / (b * Di) * c

def calc_q_switch(qi, Di, b, t_switch):
    # Calculates rate when the switch from hyperbolic to exponential decline occurs
    # Applicable only for modified hyperbolic declines
    # INPUTS:
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    #   t_switch                Time to switch from hyperbolic to exponential (years)
    # OUTPUTS:
    #   q_switch                Rate when switch from hyperbolic to exponential occurs

    c = helpers.read_settings()['days_in_year']
    return qi * (1 + b * Di * t_switch * (1 / c)) ** (-1 / b)

def terminal_switch(qi, Di, b, Dt, Di_type = 'nominal', Dt_type = 'nominal'):
    # Packages calculations for hyperbolic to exponential transition
    # Applicable only for modified hyperbolic declines
    # INPUTS:
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #                           ***Note*** Secant-effective Di input will work
    #                           if Di_type is set to 'secant'
    #   b                       b-factor
    #   Dt                      Terminal decline rate
    #   Di_type                 Initial decline rate type, default 'nominal'
    # OUTPUTS:
    #   t_switch                Time to switch from hyperbolic to exponential (years)
    #   q_switch                Rate when switch from hyperbolic to exponential occurs

    if Di_type == 'secant':
        Di = helpers.secant_to_nominal(Di, 'hyperbolic', b = b)
    
    if Dt_type == 'secant':
        Dt = helpers.secant_to_nominal(Dt, 'exponential')
    
    t_switch = calc_t_switch(Di, b, Dt)
    q_switch = calc_q_switch(qi, Di, b, t_switch)

    return t_switch, q_switch