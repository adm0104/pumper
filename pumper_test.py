import unittest
import decline_rate_conversions as drc

class test_decline(unittest.TestCase):
    def test_secant_to_nominal(self):
        # Test exponential decline calc     (1-3)
        self.assertEqual(round(drc.secant_to_nominal(0.05, 'exponential'), 4), 0.0513)
        self.assertEqual(round(drc.secant_to_nominal(0, 'exponential'), 4), 0)
        self.assertEqual(round(drc.secant_to_nominal(-0.1, 'exponential'), 4), -0.0953)
        # Test harmonic decline calc        (4-6)
        self.assertEqual(round(drc.secant_to_nominal(0.05, 'harmonic'), 4), 0.0526)
        self.assertEqual(round(drc.secant_to_nominal(0, 'harmonic'), 4), 0)
        self.assertEqual(round(drc.secant_to_nominal(-0.1, 'harmonic'), 4), -0.0909)
        # Test hyperbolic decline calc      (7-12)
        #   use b = 2
        self.assertEqual(round(drc.secant_to_nominal(0.05, 'hyperbolic', b = 2), 4), 0.0540)
        self.assertEqual(round(drc.secant_to_nominal(0, 'hyperbolic', b = 2), 4), 0)
        self.assertEqual(round(drc.secant_to_nominal(-0.1, 'hyperbolic', b = 2), 4), -0.0868)
        #   use b = 0 (mirrors harmonic decline)
        self.assertEqual(round(drc.secant_to_nominal(0.05, 'hyperbolic', b = 1), 4), 0.0526)
        self.assertEqual(round(drc.secant_to_nominal(0, 'hyperbolic', b = 1), 4), 0)
        self.assertEqual(round(drc.secant_to_nominal(-0.1, 'hyperbolic', b = 1), 4), -0.0909)

    def test_nominal_to_secant(self):
        # Test exponential decline calc     (13-15)
        self.assertEqual(round(drc.nominal_to_secant(0.05, 'exponential'), 4), 0.0488)
        self.assertEqual(round(drc.nominal_to_secant(0, 'exponential'), 4), 0)
        self.assertEqual(round(drc.nominal_to_secant(-0.1, 'exponential'), 4), -0.1052)
        # Test harmonic decline calc        (16-18)
        self.assertEqual(round(drc.nominal_to_secant(0.05, 'harmonic'), 4), 0.0476)
        self.assertEqual(round(drc.nominal_to_secant(0, 'harmonic'), 4), 0)
        self.assertEqual(round(drc.nominal_to_secant(-0.1, 'harmonic'), 4), -0.1111)
        # Test hyperbolic decline calc      (19-24)
        #   use b = 2
        self.assertEqual(round(drc.nominal_to_secant(0.05, 'hyperbolic', b = 2), 4), 0.0465)
        self.assertEqual(round(drc.nominal_to_secant(0, 'hyperbolic', b = 2), 4), 0)
        self.assertEqual(round(drc.nominal_to_secant(-0.1, 'hyperbolic', b = 2), 4), -0.1180)
        #   use b = 0 (mirrors harmonic decline)
        self.assertEqual(round(drc.nominal_to_secant(0.05, 'hyperbolic', b = 1), 4), 0.0476)
        self.assertEqual(round(drc.nominal_to_secant(0, 'hyperbolic', b = 1), 4), 0)
        self.assertEqual(round(drc.nominal_to_secant(-0.1, 'hyperbolic', b = 1), 4), -0.1111)

if __name__ == '__main__':
    unittest.main()