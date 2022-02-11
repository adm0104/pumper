import pandas as pd
import numpy as np
from . import decline_calculators as dca
from . import helper_functions as helpers

class case:

    def __init__(self, run_on_init = False, *args):
        
        self.settings = helpers.read_settings()
        if run_on_init:
            #insert self.fullrun equivalent here
            None

    def generate_timeseries(self):

        effective_date = pd.Period(self.settings['effective_date'], 'M')
        forecast_duration = self.settings['forecast_duration']
        timeseries_index = pd.period_range(effective_date, effective_date + forecast_duration - 1)

        timeseries_columns = [
            'days_start', 'days_end', 'entry_gas_rate', 'exit_gas_rate', 'gas_volume', 'entry_oil_rate', 'exit_oil_rate', 'oil_volume',
            'entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume'
        ]

        self.timeseries = pd.DataFrame(index = timeseries_index, columns = timeseries_columns)

        self.time_vector = np.linspace(0, forecast_duration, forecast_duration + 1) * self.settings['days_in_month']
        self.timeseries['days_start'], self.timeseries['days_end'] = helpers.vector_to_endpoints(self.time_vector)
    
    def gas_forecast(self, forecast_type, qi = None, qf = None, De = None, Dte = None, b = None):
        
        if De is not None:
            Di = helpers.secant_to_nominal(De, forecast_type, b)
        else:
            Di = None

        if Dte is not None:
            Dt = helpers.secant_to_nominal(Dte, 'exponential')
        else:
            Dt = None

        kwargs = {
            'qi': qi,
            'qf': qf,
            'Di': Di,
            'Dt': Dt,
            'b': b
        }

        dispatch_map = {
            'exponential': dca.calc_exponential_forecast,
            'harmonic': dca.calc_harmonic_forecast,
            'hyperbolic': dca.calc_hyperbolic_forecast,
            'flat': dca.calc_flat_forecast,
            'modified hyperbolic': dca.calc_mod_hyperbolic_forecast
        }

        if forecast_type == 'modified hyperbolic':
            self.t_switch, self.q_switch = helpers.terminal_switch(qi, Di, b, Dt)

        gas_forecast = dispatch_map[forecast_type](self.time_vector, **kwargs)
        self.timeseries.loc[:, ['entry_gas_rate', 'exit_gas_rate', 'gas_volume']] = gas_forecast