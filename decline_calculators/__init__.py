from .exponential import *
from .flat import *
from .harmonic import *
from .hyperbolic import *
from .mod_hyperbolic import *

# Decline calculators contains canned/pre-formatted functions for dealing with
# timeseries decline calculations
#
#   FORMAT:
#       calc_(declinetype)_forecast:
#           Wrapper function, will call rate, volume, and other calculations as
#           needed for the decline type.
#
#       calc_(declinetype)_rates:
#           Takes in timeseries and decline parameters as inputs, calculates
#           instantaneous rate at each timestep
#           After calculation of rates, will split rates into a vector of size
#           [(n - 1), 2] where n is the length of the original timeseries vector
#           This split is necessary for correct volume computation which is an
#           integral function that requires endpoints
#
#       calc_(declinetype)_volumes:
#           Takes in rate array as input, splits into vectors to separate out
#           time-indexed endpoints, and calculates the time integral between
#           endpoints
#
#           In simplified terms - calculates total production volume for each
#           row (often representing a month) in the case object's "time_vector"
#           property
#
#   ***COMMENT ON MOD_HYPERBOLIC***:
#       "mod_hyperbolic" is a special case that is absolutely necessary for reserves
#       evaluation, and includes additional functions also found in the "decline_helpers.py"
#       file. UPDATE BOTH IF YOU MAKE CHANGES TO EITHER!!!!!!
#       
#       To-do:  Find a way for users to either use "mod_hyperbolic" in isolation OR combine
#               the basic hyperbolic and exponential calculators (the way Aries does it)