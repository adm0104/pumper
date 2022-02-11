import numpy as np
from . import exponential as exp, hyperbolic as hyp
from .. import helper_functions as helpers

# mod_hyperbolic.py is the core calculator for the modified form of Arps' hyperbolic decline
#
# Specific definition of "modified Arps": 
#   Forecasts that calculate rate with Arps' hyperbolic
#   decline until the time where "terminal" decline rate is reached. At this point they carry
#   forward in time with Arps' exponential decline

def calc_mod_hyperbolic_forecast(time_vector, **kwargs):
    # Calculates modified hyperbolic decline rates and volumes, formatted for timeseries
    # dataframe in case.py
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    #   Dt                      Terminal decline rate
    # OUTPUTS:
    #   forecast                Full rate forecast as an array - 1st column
    #                           contains entry rates, 2nd column contains exit rates,
    #                           3rd column contains cumulative production volumes

    qi, Di, b, Dt = kwargs['qi'], kwargs['Di'], kwargs['b'], kwargs['Dt']
    t_switch, q_switch = terminal_switch(qi, Di, b, Dt)

    rate_vector_hyp = hyp.calc_hyperbolic_rates(time_vector[time_vector <= t_switch], qi, Di, b)
    rate_vector_exp = exp.calc_exponential_rates(time_vector[time_vector > t_switch] - t_switch, q_switch, Dt)
    rate_vector = np.concatenate([rate_vector_hyp, rate_vector_exp])
    entry_rates, exit_rates = helpers.vector_to_endpoints(rate_vector)

    vols_vector = calc_mod_hyperbolic_volumes(time_vector[time_vector <= t_switch], rate_vector_hyp, rate_vector_exp, Di, Dt, b, t_switch, q_switch)

    return np.array([entry_rates, exit_rates, vols_vector]).transpose()

def calc_mod_hyperbolic_rates(time_vector, qi, Di, Dt, b, t_switch, q_switch):
    # Calculates rates along time_vector per inputs qi and Di using Arps'
    # hyperbolic decline
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    #   t_switch                Time of switch from hyperbolic stem to exponential stem
    #   q_switch                Instantaneous rate at time of switch between stems
    # OUTPUTS:
    #   rate_vector             Vector of rates

    rate_vector_hyp = hyp.calc_hyperbolic_rates(time_vector[time_vector <= t_switch], qi, Di, b)
    rate_vector_exp = exp.calc_exponential_rates(time_vector[time_vector > t_switch] - t_switch, q_switch, Dt)
    return np.concatenate([rate_vector_hyp, rate_vector_exp])

def calc_mod_hyperbolic_volumes(time_vector_hyp, rate_vector_hyp, rate_vector_exp, Di, Dt, b, t_switch, q_switch):
    # Calculates volume integral for hyperbolic decline between rates in rate_vector_hyp and rate_vector_exp
    # This function bridges the forecasts during the month where the switch occurs, calculating the sum
    # of both the hyperbolic and exponential leg in that one month
    # INPUTS:
    #   time_vector_hyp         Instantaneous times for hyperbolic stem of forecast, in numpy array
    #   rate_vector_hyp         Instantaneous rates for hyperbolic stem of forecast, in numpy array
    #   rate_vector_exp         Instantaneous rates for exponential stem of forecast, in numpy array
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    #   t_switch                Time of switch from hyperbolic stem to exponential stem
    #   q_switch                Instantaneous rate at time of switch between stems
    # OUTPUTS:
    #   vols_vector             Vector of volumes

    vols_vector_hyperbolic = hyp.calc_hyperbolic_volumes(time_vector_hyp, rate_vector_hyp, Di, b)

    switch_month_hyp_time = np.array([time_vector_hyp[-1], t_switch])
    switch_month_hyp_rates = np.array([rate_vector_hyp[-1], q_switch])
    switch_month_hyp_vols = hyp.calc_hyperbolic_volumes(switch_month_hyp_time, switch_month_hyp_rates, Di, b)

    switch_month_exp_rates = np.array([q_switch, rate_vector_exp[0]])
    switch_month_exp_vols = exp.calc_exponential_volumes(switch_month_exp_rates, Dt)

    vol_switch = switch_month_hyp_vols + switch_month_exp_vols

    vols_vector_exponential = exp.calc_exponential_volumes(rate_vector_exp, Dt)
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