import unittest

from supertool import geo_nominatim, definitions as df


class NominatimTestsCase(unittest.TestCase):
    """
    TestCase for testing the  methods of interaction
    with http://nominatim.openstreetmap.org API
    """

    def test_get_coords(self):
        """
        verifies the correct reaction for correct address
        """

        expected_result = {
            'name': 'London, Greater London, England, SW1A 2DU, UK',
            'coordinates': {
                'lat': '51.5073219',
                'lon': '-0.1276474'
            }
        }
        self.assertDictEqual(expected_result,
                             geo_nominatim.get_coordinates('London'),
                             'result of the coordinate request does not match')

    def test_get_coords_with_wrong_argument(self):
        """
        verifies the correct reaction for incorrect address
        """

        argument = 'Londonsqwerr'
        with self.assertRaises(ValueError) as raised_exception:
            geo_nominatim.get_coordinates(argument)
        self.assertEqual(raised_exception.exception.args[0],
                         f'Incorrect address: {argument}')

    def test_get_coords_with_url_error(self):
        """
        verifies the correct reaction for server API Error
        """

        with self.assertRaises(df.ProcessError) as raised_exception:
            geo_nominatim.make_nominatim_request('London', 'error')
        # we cant use assertEqual here because the message contains
        # a unique from time to time memory address
        self.assertEqual(raised_exception.exception.args[0][0:24],
                         'Server interacting error', 'Incorrect AssertionError')
