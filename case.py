import pandas as pd
import numpy as np
import json

import decline_helpers as dca

class case:

    def __init__(self, run_on_init = False, *args):
        
        self.settings = dca.read_settings()
        if run_on_init:
            #insert self.fullrun equivalent here
            None

    def generate_timeseries(self):

        effective_date = pd.Period(self.settings['effective_date'], 'M')
        forecast_duration = self.settings['forecast_duration']
        timeseries_index = pd.period_range(effective_date, effective_date + forecast_duration - 1)

        timeseries_columns = [
            'days_start', 'days_end', 'gas_rate_start', 'gas_rate_end', 'gas_volume', 'oil_rate_start', 'oil_rate_end', 'oil_volume',
            'ngl_rate_start', 'ngl_rate_end', 'ngl_volume'
        ]

        self.timeseries = pd.DataFrame(index = timeseries_index, columns = timeseries_columns)