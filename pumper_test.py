import unittest
import decline_helpers as dca_help

class test_decline_helpers(unittest.TestCase):
    def test_secant_to_nominal(self):
        # Test exponential decline calc                         (1-3)
        self.assertEqual(round(dca_help.secant_to_nominal(0.05, 'exponential'), 4), 0.0513)
        self.assertEqual(round(dca_help.secant_to_nominal(0, 'exponential'), 4), 0)
        self.assertEqual(round(dca_help.secant_to_nominal(-0.1, 'exponential'), 4), -0.0953)
        # Test harmonic decline calc                            (4-6)
        self.assertEqual(round(dca_help.secant_to_nominal(0.05, 'harmonic'), 4), 0.0526)
        self.assertEqual(round(dca_help.secant_to_nominal(0, 'harmonic'), 4), 0)
        self.assertEqual(round(dca_help.secant_to_nominal(-0.1, 'harmonic'), 4), -0.0909)
        # Test hyperbolic decline calc                          (7-12)
        #   use b = 2
        self.assertEqual(round(dca_help.secant_to_nominal(0.05, 'hyperbolic', b = 2), 4), 0.0540)
        self.assertEqual(round(dca_help.secant_to_nominal(0, 'hyperbolic', b = 2), 4), 0)
        self.assertEqual(round(dca_help.secant_to_nominal(-0.1, 'hyperbolic', b = 2), 4), -0.0868)
        #   use b = 0 (mirrors harmonic decline)
        self.assertEqual(round(dca_help.secant_to_nominal(0.05, 'hyperbolic', b = 1), 4), 0.0526)
        self.assertEqual(round(dca_help.secant_to_nominal(0, 'hyperbolic', b = 1), 4), 0)
        self.assertEqual(round(dca_help.secant_to_nominal(-0.1, 'hyperbolic', b = 1), 4), -0.0909)

    def test_nominal_to_secant(self):
        # Test exponential decline calc                         (13-15)
        self.assertEqual(round(dca_help.nominal_to_secant(0.05, 'exponential'), 4), 0.0488)
        self.assertEqual(round(dca_help.nominal_to_secant(0, 'exponential'), 4), 0)
        self.assertEqual(round(dca_help.nominal_to_secant(-0.1, 'exponential'), 4), -0.1052)
        # Test harmonic decline calc                            (16-18)
        self.assertEqual(round(dca_help.nominal_to_secant(0.05, 'harmonic'), 4), 0.0476)
        self.assertEqual(round(dca_help.nominal_to_secant(0, 'harmonic'), 4), 0)
        self.assertEqual(round(dca_help.nominal_to_secant(-0.1, 'harmonic'), 4), -0.1111)
        # Test hyperbolic decline calc                          (19-24)
        #   use b = 2
        self.assertEqual(round(dca_help.nominal_to_secant(0.05, 'hyperbolic', b = 2), 4), 0.0465)
        self.assertEqual(round(dca_help.nominal_to_secant(0, 'hyperbolic', b = 2), 4), 0)
        self.assertEqual(round(dca_help.nominal_to_secant(-0.1, 'hyperbolic', b = 2), 4), -0.1180)
        #   use b = 0 (mirrors harmonic decline)
        self.assertEqual(round(dca_help.nominal_to_secant(0.05, 'hyperbolic', b = 1), 4), 0.0476)
        self.assertEqual(round(dca_help.nominal_to_secant(0, 'hyperbolic', b = 1), 4), 0)
        self.assertEqual(round(dca_help.nominal_to_secant(-0.1, 'hyperbolic', b = 1), 4), -0.1111)

    def test_read_settings(self):
        settings = dca_help.read_settings()
        # Test that settings file reads as a dictionary         (25)
        self.assertTrue(type(settings) == dict)
        # Test that important settings are reasonable           (26-27)
        self.assertTrue(type(settings['days_in_year']) == float and settings['days_in_year'] >= 365 and settings['days_in_year'] <= 366)
        self.assertTrue(type(settings['days_in_month']) == float and settings['days_in_month'] >= 26 and settings['days_in_month'] <= 31)

    def test_switch_functions(self):
        settings = dca_help.read_settings()
        t_switch = dca_help.calc_t_switch(0.45, 2, 0.05) * (settings['days_in_year'] / 365.25)
        # Test standard functionality of calc_t_switch          (28)
        self.assertEqual(round(t_switch, 4), 3246.6667)
        # Test standard functionality of calc_q_switch          (29)
        self.assertEqual(round(dca_help.calc_q_switch(500, 0.45, 2, t_switch), 4), 166.6667, 'will fail if t_switch test fails')
        # Test terminal_switch standard functionality           (30-31)
        t_switch, q_switch = dca_help.terminal_switch(500, 0.45, 2, 0.05)
        self.assertEqual(round(t_switch, 4), 3246.6667)
        self.assertEqual(round(q_switch, 4), 166.6667)
        # Test terminal_switch functionality with secant Di     (32-33)
        t_switch, q_switch = dca_help.terminal_switch(500, 0.45, 2, 0.05, Di_type = 'secant')
        self.assertEqual(round(t_switch, 4), 3494.0941)
        self.assertEqual(round(q_switch, 4), 104.1263)
        # Test terminal_switch functionality with secant Dt     (34-35)
        t_switch, q_switch = dca_help.terminal_switch(500, 0.45, 2, 0.05, Dt_type = 'secant')
        self.assertEqual(round(t_switch, 4), 3154.5736)
        self.assertEqual(round(q_switch, 4), 168.8084)


if __name__ == '__main__':
    unittest.main()