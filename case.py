import pandas as pd
import numpy as np
from . import decline_calculators as dca
from . import helper_functions as helpers

class case:

    def __init__(self, run_on_init = False):
        
        self.settings = helpers.read_settings()
        if run_on_init:
            #insert self.fullrun equivalent here
            None 

    def generate_timeseries(self):

        self.effective_date     = pd.Period(self.settings['effective_date'], 'M')
        self.forecast_duration  = self.settings['forecast_duration']
        timeseries_index        = pd.period_range(self.effective_date, self.effective_date + self.forecast_duration - 1)

        timeseries_columns = [
            'month', 'days_start', 'days_end', 'entry_gas_rate', 'exit_gas_rate', 'gas_volume', 'entry_oil_rate', 'exit_oil_rate', 'oil_volume',
            'entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume', 'entry_water_rate', 'exit_water_rate', 'water_volume', 'oil_price', 'gas_price',
            'oil_diff', 'gas_diff', 'ngl_diff', 'oil_price_real', 'gas_price_real', 'ngl_price_real', 'oil_revenue', 'gas_revenue', 'ngl_revenue',
            'fixed_opex', 'oil_opex', 'gas_opex', 'ngl_opex', 'water_opex', 'other_opex'
        ]

        self.timeseries = pd.DataFrame(index = timeseries_index, columns = timeseries_columns).fillna(0)

        self.timeseries['month'] = np.linspace(1, self.forecast_duration, self.forecast_duration)
        self.time_vector = np.linspace(0, self.forecast_duration, self.forecast_duration + 1) * self.settings['days_in_month']
        self.timeseries['days_start'], self.timeseries['days_end'] = helpers.vector_to_endpoints(self.time_vector)
    
    def generate_forecast(self, phase = None, forecast_type = 'exponential', qi = None, qf = None, De = None, Dte = None, b = None, start = None, stop = None):
        
        Di, Dt = helpers.parse_declines(De, Dte, b, forecast_type)
        start, stop, time_vector_slice = helpers.slice_time_vector(start, stop, self.time_vector)

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

        forecast = dispatch_map[forecast_type](time_vector_slice, **kwargs)
        self.add_forecast(phase, forecast, start = start, stop = stop)

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

    def add_forecast(self, phase, forecast, start = None, stop = None):

        if start is None and stop is None:
            if phase == 'gas':
                self.timeseries.loc[:, ['entry_gas_rate', 'exit_gas_rate', 'gas_volume']] += forecast
            elif phase == 'oil':
                self.timeseries.loc[:, ['entry_oil_rate', 'exit_oil_rate', 'oil_volume']] += forecast
            elif phase == 'ngl':
                self.timeseries.loc[:, ['entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume']] += forecast
            elif phase == 'water':
                self.timeseries.loc[:, ['entry_water_rate', 'exit_water_rate', 'water_volume']] += forecast
        else:
            if phase == 'gas':
                self.timeseries.loc[start:stop, ['entry_gas_rate', 'exit_gas_rate', 'gas_volume']] += forecast
            elif phase == 'oil':
                self.timeseries.loc[start:stop, ['entry_oil_rate', 'exit_oil_rate', 'oil_volume']] += forecast
            elif phase == 'ngl':
                self.timeseries.loc[start:stop, ['entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume']] += forecast
            elif phase == 'water':
                self.timeseries.loc[start:stop, ['entry_water_rate', 'exit_water_rate', 'water_volume']] += forecast

    def import_default_pricing(self):

        self.pricing = pd.DataFrame(helpers.read_default_pricing()).to_numpy()
        self.timeseries.loc[:, ['oil_price', 'gas_price', 'oil_diff', 'gas_diff', 'ngl_diff']] = self.pricing
        self.calc_realized_pricing()

    def calc_realized_pricing(self):
        self.timeseries.loc[:, ['oil_price_real']] = self.timeseries['oil_price'] + self.timeseries['oil_diff']
        self.timeseries.loc[:, ['gas_price_real']] = self.timeseries['gas_price'] + self.timeseries['gas_diff']
        self.timeseries.loc[:, ['ngl_price_real']] = self.timeseries['oil_price'] * self.timeseries['ngl_diff']

    def import_pricing(self, format, price_file = None):
        # To-do:    Decide how many price deck formats to allow as inputs
        #           Currently allowing dataframe, excel, text
        #           Flesh out kwargs and dispatch map for different options
        #           Resolve pathing question - prefer for this and specific 
        #           imports to be helper functions but pathing is obtuse if
        #           it's structured that way
        dispatch_map = {
            'df': self.import_pricing_df,
            'xls': self.import_pricing_xls,
            'txt': self.import_pricing_txt
        }
        self.pricing = dispatch_map[format](price_file)
    
    def import_pricing_df(self, price_file):
        # To-do:    Come up with a format for pricing dataframes
        #           Come up with a reasonable way for a user to build a price deck into a dataframe
        #           Should be able to go user DF -> object property DF -> timeseries columns
        #           What about xls/txt/json/parquet -> DF???
        None
    
    def import_pricing_xls(self, price_file):
        # To-do:    Come up with a format for pricing spreadsheets
        #           Try to allow user to input in any format allowed in Aries
        #           Build parser function
        #           Include a guide or example in README
        None

    def import_pricing_txt(self, price_file):
        # To-do:    Come up with a format for pricing .txt docs
        #           Try to make this similar to Aries format, is limited with .txt
        #           Build parser function
        #           Include a guide or example in README
        None

    def calc_sales_revenue(self):
        self.timeseries.loc[:, ['oil_revenue']] = self.timeseries['oil_volume'] * self.timeseries['oil_price_real']
        self.timeseries.loc[:, ['gas_revenue']] = self.timeseries['gas_volume'] * self.timeseries['gas_price_real']
        self.timeseries.loc[:, ['ngl_revenue']] = self.timeseries['ngl_volume'] * self.timeseries['ngl_price_real']

    def assign_fixed_opex(self, input_type, input):
        
        dispatch_map = {
            'flat': self.flat_fixed_opex,
            'linear': self.linear_fixed_opex,
            'dependent': self.dependent_fixed_opex,
            'import': self.import_fixed_opex
        }

        dispatch_map[input_type](input)

    def flat_fixed_opex(self, opex):
        #   To-do:  Actually build this
        None
    
    def linear_fixed_opex(self, opex):
        #   To-do:  Actually build this
        None

    def dependent_fixed_opex(self, opex):
        #   To-do:  Actually build this
        None

    def import_fixed_opex(self, opex):
        #   To-do:  Actually build this
        None