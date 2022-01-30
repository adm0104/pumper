import numpy as np
import pandas as pd
import json

def secant_to_nominal(De, decline_type, b = None):
    # Converts secant effective decline to nominal decline
    # INPUTS:
    #   De                      Effective decline rate in secant effective form
    #   decline_type            Decline curve decline type
    #   b                       b-factor, used only if applicable (default None)
    # OUTPUTS:
    #   Di                      Nominal decline rate

    if decline_type == 'exponential':
        Di = -np.log(1 - De)
    elif decline_type == 'harmonic':
        Di = De / (1 - De)
    elif decline_type =='hyperbolic':
        Di = (1 / b) * (1 / (1 - De) ** b - 1)
    return Di

def nominal_to_secant(Di, decline_type, b = None):
    # Converts nominal decline to secant effective decline
    # INPUTS:
    #   Di                      Nominal decline rate
    #   decline_type            Decline curve decline type
    #   b                       b-factor, used only if applicable (default None)
    # OUTPUTS:
    #   De                      Effective decline rate in secant effective form

    if decline_type == 'exponential':
        De = 1 - np.exp(-Di)
    elif decline_type == 'harmonic':
        De = Di / (1 + Di)
    elif decline_type =='hyperbolic':
        De = 1 - 1 / (1 + b * Di) ** (1 / b)
    return De

def read_settings():
    # Reads settings json file (settings.json)
    # Settings contains unit conversion constants, other user preferences
    # INPUTS:
    #   None
    # OUTPUTS:
    #   settings                Dictionary of user settings

    with open('settings.json') as f:
        return json.load(f)

def calc_t_switch(Di, b, Dt):
    # Calculates point in time when the switch from hyperbolic to exponential decline occurs
    # Applicable only for modified hyperbolic declines
    # INPUTS:
    #   Di                      Nominal initial decline rate
    #   b                       b-factor
    #   Dt                      Terminal decline rate
    # OUTPUTS:
    #   t_switch                Time to switch from hyperbolic to exponential (years)

    c = read_settings()['days_in_year']
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

    c = read_settings()['days_in_year']
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
        Di = secant_to_nominal(Di, 'hyperbolic', b = b)
    
    if Dt_type == 'secant':
        Dt = secant_to_nominal(Dt, 'exponential')
    
    t_switch = calc_t_switch(Di, b, Dt)
    q_switch = calc_q_switch(qi, Di, b, t_switch)

    return t_switch, q_switch

def calc_exponential_forecast(time_vector = None, qi = None, Di = None):
    # Calculates exponential decline, formatted for insertion into timeseries
    # dataframe in case.py
    # INPUTS:
    #   time_vector             Instantaneous times for forecast, in numpy array\
    #   qi                      Initial rate
    #   Di                      Nominal initial decline rate
    # OUTPUTS:
    #   gas_forecast            Full rate forecast as an array - 1st column
    #                           contains entry rates, 2nd column contains exit rates,
    #                           3rd column contains cumulative production volumes

    c = read_settings()['days_in_year']
    rate_vector = qi * np.exp(-Di * time_vector * (1 / c))
    vols_vector = (rate_vector[:-1] - rate_vector[1:]) / Di
    return np.array([rate_vector[:-1], rate_vector[1:], vols_vector]).transpose()