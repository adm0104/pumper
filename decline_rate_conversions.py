import numpy as np

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