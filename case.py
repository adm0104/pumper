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

        self.effective_date = pd.Period(self.settings['effective_date'], 'M')
        self.forecast_duration = self.settings['forecast_duration']
        timeseries_index = pd.period_range(self.effective_date, self.effective_date + self.forecast_duration - 1)

        timeseries_columns = [
            'month', 'days_start', 'days_end', 'entry_gas_rate', 'exit_gas_rate', 'gas_volume', 'entry_oil_rate', 'exit_oil_rate', 'oil_volume',
            'entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume', 'entry_water_rate', 'exit_water_rate', 'water_volume', 'oil_price', 'gas_price',
            'oil_diff', 'gas_diff', 'ngl_diff'
        ]

        self.timeseries = pd.DataFrame(index = timeseries_index, columns = timeseries_columns).fillna(0)

        self.timeseries['month'] = np.linspace(1, self.forecast_duration, self.forecast_duration)
        self.time_vector = np.linspace(0, self.forecast_duration, self.forecast_duration + 1) * self.settings['days_in_month']
        self.timeseries['days_start'], self.timeseries['days_end'] = helpers.vector_to_endpoints(self.time_vector)
    
    def generate_forecast(self, phase = None, forecast_type = 'exponential', qi = None, qf = None, De = None, Dte = None, b = None):
        
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
            'b': b,
            'phase': phase
        }

        dispatch_map = {
            'exponential': dca.calc_exponential_forecast,
            'harmonic': dca.calc_harmonic_forecast,
            'hyperbolic': dca.calc_hyperbolic_forecast,
            'flat': dca.calc_flat_forecast,
            'modified hyperbolic': dca.calc_mod_hyperbolic_forecast
        }

        forecast = dispatch_map[forecast_type](self.time_vector, **kwargs)
        self.add_forecast(phase, forecast)

    def ratio_forecast(self, ratio_phase, base_phase, ratio):
        
        if base_phase == 'gas':
            forecast = self.timeseries.loc[:, ['entry_gas_rate', 'exit_gas_rate', 'gas_volume']].to_numpy() * ratio
        elif base_phase == 'oil':
            forecast = self.timeseries.loc[:, ['entry_oil_rate', 'exit_oil_rate', 'oil_volume']].to_numpy() * ratio
        elif base_phase == 'ngl':
            forecast = self.timeseries.loc[:, ['entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume']].to_numpy() * ratio
        elif base_phase == 'water':
            forecast = self.timeseries.loc[:, ['entry_water_rate', 'exit_water_rate', 'water_volume']].to_numpy() * ratio

        self.add_forecast(ratio_phase, forecast)

    def add_forecast(self, phase, forecast):

        if phase == 'gas':
            self.timeseries.loc[:, ['entry_gas_rate', 'exit_gas_rate', 'gas_volume']] += forecast
        elif phase == 'oil':
            self.timeseries.loc[:, ['entry_oil_rate', 'exit_oil_rate', 'oil_volume']] += forecast
        elif phase == 'ngl':
            self.timeseries.loc[:, ['entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume']] += forecast
        elif phase == 'water':
            self.timeseries.loc[:, ['entry_water_rate', 'exit_water_rate', 'water_volume']] += forecast

    def import_default_pricing(self):
        self.pricing = pd.DataFrame(helpers.read_default_pricing()).to_numpy()
        self.timeseries.loc[:, ['oil_price', 'gas_price', 'oil_diff', 'gas_diff', 'ngl_diff']] = self.pricing

    def import_pricing_from_df(self, price_df):
        None