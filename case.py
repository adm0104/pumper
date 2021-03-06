import pandas as pd
import numpy as np
from . import decline_calculators as dca
from . import helper_functions as helpers

class case:

    def __init__(self, run_on_init = False):

        self.settings = helpers.read_settings()
        self.generate_timeseries()
        if run_on_init:
            #insert self.fullrun equivalent here
            None

    def generate_timeseries(self):

        self.effective_date         = pd.Period(self.settings['effective_date'], 'M')
        self.forecast_duration      = self.settings['forecast_duration']
        timeseries_index            = pd.period_range(self.effective_date, self.effective_date + self.forecast_duration - 1)

        timeseries_columns = [
            'month', 'days_start', 'days_end', 'working_int', 'rev_int', 'entry_gas_rate', 'exit_gas_rate', 'gas_volume', 'entry_oil_rate',
            'exit_oil_rate', 'oil_volume', 'entry_ngl_rate', 'exit_ngl_rate', 'ngl_volume', 'entry_water_rate', 'exit_water_rate', 'water_volume', 'shrink',
            'oil_price', 'gas_price', 'oil_diff', 'gas_diff', 'ngl_diff', 'oil_price_real', 'gas_price_real', 'ngl_price_real', 'gross_oil_revenue',
            'gross_gas_revenue', 'gross_ngl_revenue', 'gross_revenue', 'net_oil_volume', 'net_gas_volume', 'net_ngl_volume', 'net_water_volume', 'net_oil_revenue',
            'net_gas_revenue', 'net_ngl_revenue', 'net_revenue', 'gross_capex', 'net_capex', 'gross_fixed_opex', 'gross_oil_opex', 'gross_gas_opex',
            'gross_ngl_opex', 'gross_water_opex', 'net_fixed_opex', 'net_oil_opex', 'net_gas_opex', 'net_ngl_opex', 'net_water_opex', 'net_variable_opex',
            'net_opex', 'gross_overhead', 'net_overhead', 'sev_tax', 'ad_val_tax', 'net_tax', 'operating_profit', 'net_income', 'net_cash_flow', 
            'cum_cash_flow', 'net_pv10', 'cum_pv10'
        ]

        self.timeseries             = pd.DataFrame(index = timeseries_index, columns = timeseries_columns).fillna(0)
        self.timeseries['month']    = np.linspace(1, self.forecast_duration, self.forecast_duration)
        self.time_vector            = np.linspace(0, self.forecast_duration, self.forecast_duration + 1) * self.settings['days_in_month']

        self.timeseries['days_start'], self.timeseries['days_end'] = helpers.vector_to_endpoints(self.time_vector)

    def assign_to_timeseries(self, item, column, start = None, stop = None):

        # To-do:    Get rid of if/else by being more intelligent with start/stop
        #           indices - low priority
        if start is None and stop is None:
            self.timeseries.loc[:, column] = item
        else:
            self.timeseries.loc[start:stop, column] = item

    def add_to_timeseries(self, item, column, start = None, stop = None):

        # To-do:    Get rid of if/else by being more intelligent with start/stop
        #           indices - low priority
        if start is None and stop is None:
            self.timeseries.loc[:, column] += item
        else:
            self.timeseries.loc[start:stop, column] += item
    
    def mult_add_timeseries(self, ratio, target_column, base_column, start = None, stop = None):

        # To-do:    Get rid of if/else by being more intelligent with start/stop
        #           indices - low priority
        if start is None and stop is None:
            self.timeseries.loc[:, target_column] += self.timeseries.loc[:, base_column] * ratio
        else:
            self.timeseries.loc[start:stop, target_column] += self.timeseries.loc[start:stop, base_column] * ratio

    def mult_add_cols_timeseries(self, mult_column, target_column, base_column, start = None, stop = None):

        # To-do:    Get rid of if/else by being more intelligent with start/stop
        #           indices - low priority
        if start is None and stop is None:
            self.timeseries.loc[:, target_column] += self.timeseries.loc[:, base_column] * self.timeseries.loc[:, mult_column]
        else:
            self.timeseries.loc[start:stop, target_column] += self.timeseries.loc[start:stop, base_column] * self.timeseries.loc[start:stop, mult_column]
    
    def generate_forecast(self, phase = None, forecast_type = 'exponential', qi = None, qf = None, De = None, Dte = None, b = None, start = None, stop = None):
        
        Di, Dt = helpers.parse_declines(De, Dte, b, forecast_type)
        start, stop, time_vector_slice = helpers.slice_time_vector(start, stop, self.time_vector)

        kwargs = {
            'qi':       qi,
            'qf':       qf,
            'Di':       Di,
            'Dt':       Dt,
            'b':        b,
            'phase':    phase
        }

        dispatch_map = {
            'exponential':          dca.calc_exponential_forecast,
            'harmonic':             dca.calc_harmonic_forecast,
            'hyperbolic':           dca.calc_hyperbolic_forecast,
            'flat':                 dca.calc_flat_forecast,
            'modified hyperbolic':  dca.calc_mod_hyperbolic_forecast
        }

        forecast = dispatch_map[forecast_type](time_vector_slice, **kwargs)
        self.add_forecast(phase, forecast, start = start, stop = stop)

    def add_forecast(self, phase, forecast, start = None, stop = None):

        self.add_to_timeseries(forecast[:, 0], 'entry_' + phase + '_rate', start, stop)
        self.add_to_timeseries(forecast[:, 1], 'exit_' + phase + '_rate', start, stop)
        self.add_to_timeseries(forecast[:, 2], phase + '_volume', start, stop)

    def ratio_forecast(self, ratio_phase, base_phase, ratio, start = None, stop = None):
        
        self.mult_add_timeseries(ratio, 'entry_' + ratio_phase + '_rate', 'entry_' + base_phase + '_rate', start, stop)
        self.mult_add_timeseries(ratio, 'exit_' + ratio_phase + '_rate', 'exit_' + base_phase + '_rate', start, stop)
        self.mult_add_timeseries(ratio, ratio_phase + '_volume', base_phase + '_volume', start, stop)

    def shrink(self, shrink):

        self.timeseries['shrink'] = shrink

    def import_default_pricing(self):

        pricing = pd.DataFrame(helpers.read_default_pricing()).to_numpy()
        self.timeseries.loc[:, ['oil_price', 'gas_price', 'oil_diff', 'gas_diff', 'ngl_diff']] = pricing
        self.calc_realized_pricing()

    def flat_pricing(self, oil_price, oil_diff, gas_price, gas_diff, ngl_diff):

        self.timeseries['oil_price']            = oil_price
        self.timeseries['oil_diff']             = oil_diff
        self.timeseries['gas_price']            = gas_price
        self.timeseries['gas_diff']             = gas_diff
        self.timeseries['ngl_diff']             = ngl_diff
        self.calc_realized_pricing()

    def calc_realized_pricing(self):

        self.timeseries['oil_price_real']       = self.timeseries['oil_price'] + self.timeseries['oil_diff']
        self.timeseries['gas_price_real']       = self.timeseries['gas_price'] + self.timeseries['gas_diff']
        self.timeseries['ngl_price_real']       = self.timeseries['oil_price'] * self.timeseries['ngl_diff']

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

    def assign_ownership(self, working_int, rev_int, type = 'frac', start = None, stop = None):
       
        if type == 'percent':
            working_int     /= 100
            rev_int         /= 100

        self.assign_to_timeseries(working_int, 'working_int', start, stop)
        self.assign_to_timeseries(rev_int, 'rev_int', start, stop)

    def calc_sales_revenue(self):

        self.timeseries['gross_oil_revenue']        = self.timeseries['oil_volume'] * self.timeseries['oil_price_real']
        self.timeseries['gross_gas_revenue']        = self.timeseries['gas_volume'] * self.timeseries['gas_price_real'] * self.timeseries['shrink']
        self.timeseries['gross_ngl_revenue']        = self.timeseries['ngl_volume'] * self.timeseries['ngl_price_real']
        self.timeseries['gross_revenue']            = self.timeseries.loc[:, ['gross_oil_revenue', 'gross_gas_revenue', 'gross_ngl_revenue']].sum(axis = 1)

        self.timeseries['net_oil_revenue']          = self.timeseries['gross_oil_revenue'] * self.timeseries['rev_int']
        self.timeseries['net_gas_revenue']          = self.timeseries['gross_gas_revenue'] * self.timeseries['rev_int']
        self.timeseries['net_ngl_revenue']          = self.timeseries['gross_ngl_revenue'] * self.timeseries['rev_int']
        self.timeseries['net_revenue']              = self.timeseries.loc[:, ['net_oil_revenue', 'net_gas_revenue', 'net_ngl_revenue']].sum(axis = 1)

    def calc_net_production(self):

        self.timeseries['net_oil_volume']           = self.timeseries['oil_volume'] * self.timeseries['rev_int']
        self.timeseries['net_gas_volume']           = self.timeseries['gas_volume'] * self.timeseries['rev_int'] * self.timeseries['shrink']
        self.timeseries['net_ngl_volume']           = self.timeseries['ngl_volume'] * self.timeseries['rev_int']
        self.timeseries['net_water_volume']         = self.timeseries['water_volume'] * self.timeseries['rev_int']

    def assign_capex(self, amount, type = 'gross', month = None):

        if month is None:
            month = self.settings['effective_date']

        if type == 'gross':
            self.timeseries.loc[month, 'gross_capex']    += amount
            self.timeseries.loc[month, 'net_capex']      += amount * self.timeseries.loc[month, 'working_int']
        elif type == 'net':
            self.timeseries.loc[month, 'gross_capex']    += amount / self.timeseries.loc[month, 'working_int']
            self.timeseries.loc[month, 'net_capex']      += amount

    def assign_fixed_opex(self, input, input_type, start = None, stop = None):
        
        dispatch_map = {
            'flat': self.flat_fixed_opex,
            'linear': self.linear_fixed_opex,
            'import': self.import_fixed_opex
        }

        dispatch_map[input_type](input, start, stop)
        self.calc_net_opex()

    def flat_fixed_opex(self, opex, start = None, stop = None):

        self.add_to_timeseries(opex, 'gross_fixed_opex', start, stop)
        self.mult_add_timeseries(opex, 'net_fixed_opex', 'working_int', start, stop)
    
    def linear_fixed_opex(self, opex):

        #   To-do:  Actually build this
        #           Make the fixed cost a linear function
        #           Maybe add ability to do other functions? Might not be useful...

        None

    def import_fixed_opex(self, opex):

        #   To-do:  Actually build this
        #           Going to need multiple functions for multiple file types like w/
        #           pricing

        None

    def assign_overhead(self, amount, start = None, stop = None):

        self.add_to_timeseries(amount, 'gross_overhead', start, stop)
        self.timeseries['net_overhead'] = self.timeseries.loc[:, ['rev_int', 'gross_overhead']].product(axis = 1)

    def assign_variable_opex(self, ratio, base_phase, start = None, stop = None):
        
        self.mult_add_timeseries(ratio, 'gross_' + base_phase + '_opex', base_phase + '_volume', start, stop)
        self.mult_add_cols_timeseries('working_int', 'net_' + base_phase + '_opex', 'gross_' + base_phase + '_opex', start, stop)
        self.timeseries['gross_gas_opex'] = self.timeseries['gross_gas_opex'] * self.timeseries['shrink']
        self.timeseries['net_gas_opex'] = self.timeseries['net_gas_opex'] * self.timeseries['shrink']
        self.calc_net_opex()

    def calc_net_opex(self):
        
        self.timeseries['net_variable_opex']        = self.timeseries.loc[:, ['net_oil_opex', 'net_gas_opex', 'net_ngl_opex', 'net_water_opex']].sum(axis = 1)
        self.timeseries['net_opex']                 = self.timeseries.loc[:, ['net_fixed_opex', 'net_variable_opex']].sum(axis = 1)

    def assign_tax(self, ad_val_rate, sev_rate, deductible = True, start = None, stop = None):
        
        # To-do:    The two types of tax are inconsistent with each other in how they handle start/stop dates
        #           Decide whether we need start/stop on tax, and make this method consistent
        self.mult_add_timeseries(sev_rate, 'sev_tax', 'net_revenue', start, stop)

        if deductible:
            if start is None and stop is None:
                self.timeseries.loc[:, 'ad_val_tax'] = ad_val_rate * (self.timeseries.loc[:, 'net_revenue'] - self.timeseries.loc[:, 'sev_tax'])
            else:
                self.timeseries.loc[start:stop, 'ad_val_tax'] = ad_val_rate * (self.timeseries.loc[start:stop, 'net_revenue'] - self.timeseries.loc[start:stop, 'sev_tax'])
        else:
            self.mult_add_timeseries(ad_val_rate, 'ad_val_tax', 'net_revenue', start, stop)
        
        self.timeseries['net_tax'] = self.timeseries.loc[:, ['sev_tax', 'ad_val_tax']].sum(axis = 1)

    def calc_cash_flow(self):

        self.timeseries['operating_profit']         = self.timeseries['net_revenue'] - self.timeseries['net_opex'] - self.timeseries['net_tax']
        self.timeseries['net_income']               = self.timeseries['operating_profit'] - self.timeseries['net_overhead']
        self.timeseries['net_cash_flow']            = self.timeseries['net_income'] - self.timeseries['net_capex']
        self.timeseries['cum_cash_flow']            = self.timeseries['net_cash_flow'].cumsum()
        self.timeseries['net_pv10']                 = self.timeseries['net_cash_flow'] / (1.1 ** (self.timeseries['days_start'] / self.settings['days_in_year']))
        self.timeseries['cum_pv10']                 = self.timeseries['net_pv10'].cumsum()

    def modify_loss_function(self, loss_function):
        
        self.settings['loss_function'] = loss_function

    def calc_end_of_life(self):

        if self.settings['loss_function'] == 'NO':
            self.end_of_life = self.timeseries[self.timeseries['operating_profit'] <= 0].index[0]

        elif self.settings['loss_function'] == 'BFIT':
            self.end_of_life = self.timeseries[self.timeseries['net_income'] <= 0].index[0]

        elif self.settings['loss_function'] == 'OK':
            self.end_of_life = self.timeseries.index[-1:]

    def impose_end_of_life(self, zero = False):

        self.calc_end_of_life()
        if zero:
            self.timeseries.loc[self.end_of_life:, 'entry_gas_rate':] = 0
        else:
            self.timeseries = self.timeseries.drop(self.timeseries.loc[self.end_of_life:].index)

    def generate_oneline(self, name):

        self.oneline = pd.DataFrame(
            index = [name],
            data = self.calc_oneline_data()
        )

    def calc_oneline_data(self):

        oneline_data = {
            'working_int':          self.timeseries['working_int'].max(),
            'rev_int':              self.timeseries['rev_int'].max(),
            'gross_capex':          self.timeseries['gross_capex'].sum(),
            'net_capex':            self.timeseries['net_capex'].sum(),
            'peak_oil_rate':        self.timeseries['entry_oil_rate'].max(),
            'peak_gas_rate':        self.timeseries['entry_gas_rate'].max(),
            'peak_ngl_rate':        self.timeseries['entry_ngl_rate'].max(),
            'peak_water_rate':      self.timeseries['entry_water_rate'].max(),
            'gross_oil':            self.timeseries['oil_volume'].sum(),
            'gross_gas':            self.timeseries['gas_volume'].sum(),
            'gross_ngl':            self.timeseries['ngl_volume'].sum(),
            'gross_water':          self.timeseries['water_volume'].sum(),
            'gross_oil_revenue':    self.timeseries['gross_oil_revenue'].sum(),
            'gross_gas_revenue':    self.timeseries['gross_gas_revenue'].sum(),
            'gross_ngl_revenue':    self.timeseries['gross_ngl_revenue'].sum(),
            'gross_revenue':        self.timeseries['gross_revenue'].sum(),
            'net_oil_volume':       self.timeseries['net_oil_volume'].sum(),
            'net_gas_volume':       self.timeseries['net_gas_volume'].sum(),
            'net_ngl_volume':       self.timeseries['net_ngl_volume'].sum(),
            'net_water_volume':     self.timeseries['net_water_volume'].sum(),
            'net_oil_revenue':      self.timeseries['net_oil_revenue'].sum(),
            'net_gas_revenue':      self.timeseries['net_gas_revenue'].sum(),
            'net_ngl_revenue':      self.timeseries['net_ngl_revenue'].sum(),
            'net_revenue':          self.timeseries['net_revenue'].sum(),
            'gross_fixed_opex':     self.timeseries['gross_fixed_opex'].sum(),
            'gross_oil_opex':       self.timeseries['gross_oil_opex'].sum(),
            'gross_gas_opex':       self.timeseries['gross_gas_opex'].sum(),
            'gross_ngl_opex':       self.timeseries['gross_ngl_opex'].sum(),
            'gross_water_opex':     self.timeseries['gross_water_opex'].sum(),
            'net_fixed_opex':       self.timeseries['net_fixed_opex'].sum(),
            'net_oil_opex':         self.timeseries['net_oil_opex'].sum(),
            'net_gas_opex':         self.timeseries['net_gas_opex'].sum(),
            'net_ngl_opex':         self.timeseries['net_ngl_opex'].sum(),
            'net_water_opex':       self.timeseries['net_water_opex'].sum(),
            'net_variable_opex':    self.timeseries['net_variable_opex'].sum(),
            'net_opex':             self.timeseries['net_opex'].sum(),
            'gross_overhead':       self.timeseries['gross_overhead'].sum(),
            'net_overhead':         self.timeseries['net_overhead'].sum(),
            'sev_tax':              self.timeseries['sev_tax'].sum(),
            'ad_val_tax':           self.timeseries['ad_val_tax'].sum(),
            'net_tax':              self.timeseries['net_tax'].sum(),
            'operating_profit':     self.timeseries['operating_profit'].sum(),
            'net_income':           self.timeseries['net_income'].sum(),
            'net_cash_flow':        self.timeseries['net_cash_flow'].sum(),
            'net_pv10':             self.timeseries['net_pv10'].sum(),
            #'end_of_life':          self.end_of_life
        }
        
        return oneline_data
