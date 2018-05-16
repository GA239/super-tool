from io import StringIO
import unittest
from unittest.mock import Mock, patch

from supertool import weather, definitions as df


class WeatherTestsCase(unittest.TestCase):
    """
    TestCase for testing the  methods of interaction
    with http://api.openweathermap.org API
    """

    def _test_bad_request(self, postfix):
        """
        sends an incorrect request and verifies
        that the response is correctly processed

        :param postfix: api service of openweathermap
        :return: None
        """

        with self.assertRaises(df.ResponseError) as raised_exception:
            weather.get_weather('Londonx', postfix)
        self.assertEqual(raised_exception.exception.args[0],
                         'Code: 404 -- city not found')

    @staticmethod
    def _get_weather_block(description: str) -> dict:
        """
        Creates a fake response with weather information

        :param description: weather description
        :return: fake response with weather information
        """
        return {
                "weather": [
                    {"description": description}
                ],
                "main": {
                    "temp": 13.81,
                    "pressure": 1010,
                    "humidity": 67,
                },
                "clouds": {
                    "all": 12
                },
                "wind": {
                    "speed": 2.1,
                    "deg": 270
                },
                "sys": {
                    "country": "GB",
                },
                "name": "London",
            }

    def _getting_weather_when_response_is_ok(self, address: str or dict) -> None:
        """
        Verifies that the correct response
        is correctly processed

        :param address: address which can be
        string address or geo coordinates
        :return:
        """

        with patch('requests.get') as mock_get:
            response = self._get_weather_block("clear sky")
            # Configure the mock to return a response with an OK status code.
            # Also, the mock should have a `json()` method.
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = response

            # Call the service, which will send a request to the server.
            result = weather.get_weather(address, 'weather')

        expected_report = (
            '--------------------------------------------------\n'
            '          Current weather in London (GB)          \n'
            '--------------------------------------------------',
            'Description                              clear sky\n'
            'temperature (Celsius):                       13.81\n'
            'pressure (hPa):                               1010\n'
            'humidity (%):                                   67\n'
            'wind speed (meter/sec):                        2.1\n'
            'cloudiness (%):                                 12'
        )
        self.assertEqual(result, expected_report, 'Incorrect weather description')

    def test_getting_weather_when_response_is_ok_address_as_str(self):
        """
        Verifies that the address entered as
        a string is correctly processed

        :return: None
        """

        self._getting_weather_when_response_is_ok('London')

    def test_getting_weather_when_response_is_ok_address_as_coords(self):
        """
        Verifies that the address entered as
        coordinates is correctly processed
        :return: None
        """

        self._getting_weather_when_response_is_ok({
            'lat': 100,
            'lon': 100
        })

    def test_incorrect_coords_key(self):
        """
        Verifies that the address entered as
        coordinates, which contains key-error
        is correctly processed
        :return: None
        """

        argument = {
            'lat': 100,
            'ldon': 100
        }
        with self.assertRaises(ValueError) as raised_exception:
            weather.get_weather(argument, 'weather')
        self.assertEqual(raised_exception.exception.args[0],
                         f'Wrong cords: {argument}!')

    def test_incorrect_coords_type(self):
        """
        Verifies that the address entered as
        coordinates, which are incorrect type
        is correctly processed
        :return: None
        """

        argument = 56
        with self.assertRaises(TypeError) as raised_exception:
            weather.get_weather(argument, 'weather')
        self.assertEqual(raised_exception.exception.args[0],
                         f'Wrong location: {argument}!')

    def test_getting_weather_when_response_is_not_ok(self):
        """
        Verifies that the response after
        incorrect request to current weather service
        is correctly processed
        :return: None
        """

        self._test_bad_request('weather')

    def test_getting_weather_forecast_when_response_is_not_ok(self):
        """
        Verifies that the response after
        incorrect request to forecast weather service
        is correctly processed
        :return: None
        """

        self._test_bad_request('forecast')

    def test_getting_weather_forecast_when_response_is_ok(self):
        """
         Verifies that the correct response
         is correctly processed

         :return: None
         """

        with patch('requests.get') as mock_get:
            response = {
                "city": {
                    "name": "London",
                    "country": "GB",
                },
                "list": [
                    self._get_weather_block("clear sky"),
                    self._get_weather_block("cloudy")
                ]
            }
            response["list"][0]["dt_txt"] = "2018-05-06 18:00:00"
            response["list"][1]["dt_txt"] = "2018-05-06 21:00:00"

            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = response

            # Call the service, which will send a request to the server.
            result = weather.get_weather('London', 'forecast')

        expected_result = (
            '--------------------------------------------------\n'
            '       The weather forecast in London (GB)        \n'
            '--------------------------------------------------',
            '               2018-05-06 18:00:00                \n'
            'Description                              clear sky\n'
            'temperature (Celsius):                       13.81\n'
            'pressure (hPa):                               1010\n'
            'humidity (%):                                   67\n'
            'wind speed (meter/sec):                        2.1\n'
            'cloudiness (%):                                 12\n'
            '               2018-05-06 21:00:00                \n'
            'Description                                 cloudy\n'
            'temperature (Celsius):                       13.81\n'
            'pressure (hPa):                               1010\n'
            'humidity (%):                                   67\n'
            'wind speed (meter/sec):                        2.1\n'
            'cloudiness (%):                                 12'
        )

        self.assertEqual(result, expected_result, 'Incorrect weather forecast')

    def _invalid_api_key(self, postfix):
        """
        sends an incorrect request (Wrong API key )and verifies
        that the response is correctly processed

        :param postfix: api service of openweathermap
        :return: None
        """

        with self.assertRaises(df.ResponseError) as raised_exception:
            weather.get_weather('London', postfix, api_key='df')
        self.assertEqual(raised_exception.exception.args[0],
                         'Code: 401 -- Invalid API key. '
                         'Please see http://openweathermap.org/faq#error401 for more info.')

    def test_invalid_api_for_current_weather(self):
        """
        Verifies invalid API key reaction
        """

        self._invalid_api_key('weather')

    def test_invalid_api_for_weather_forecast(self):
        """
        Verifies invalid API key reaction
        """

        self._invalid_api_key('forecast')

    def test_invalid_postfix(self):
        """
        Verifies invalid service reaction
        """

        with self.assertRaises(df.ResponseError) as raised_exception:
            weather.get_weather('London', 'df')
        self.assertEqual(raised_exception.exception.args[0],
                         'Code: 404 -- Internal error')

    def test_invalid_report_postfix(self):
        """
        Verifies reporter invalid service reaction
        """

        invalid_postfix = 'invalid_postfix'
        with self.assertRaises(ValueError) as raised_exception:
            weather.open_weather_reporter(invalid_postfix)
        self.assertEqual(raised_exception.exception.args[0],
                         f'Reporter for {invalid_postfix} does not fount!')

    def test_server_error(self):
        """
        Verifies invalid url reaction
        """

        with self.assertRaises(df.ProcessError) as raised_exception:
            weather.make_open_weather_request('London', 'er', "http://api.openweatyhermap.org/data/2.5/")
        # we cant use assertEqual here because the message contains
        # a unique from time to time memory address
        self.assertEqual(raised_exception.exception.args[0][0:24],
                         'Server interacting error', 'Incorrect AssertionError')

    @staticmethod
    @weather.exception_catcher
    def _decorator_tester(address, pstfix, url):
        """
        Function to test that the decorator does not correctly handle exceptions
        """

        weather.make_open_weather_request(address, pstfix, url)

    def test_assert_decorator(self):
        """
        checks that the decorator correctly handle the key-error

        :return: None
        """

        argument = {
            'lat': 100,
            'ldon': 100
        }
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self._decorator_tester(argument, 'weather', df.OPEN_WEATHER_URL)
        self.assertEqual(fake_out.getvalue().strip(),
                         f'Error in the entered data! \nWrong cords: {argument}!')

    def test_assert_decorator_process_error(self):
        """
        checks that the decorator correctly handle the url-error

        :return: None
        """

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self._decorator_tester('London', 'weather',
                                   "http://api.openweadsthermap.org/data/2.5/")
        self.assertEqual(fake_out.getvalue().strip()[0:49],
                         'Error in the process of interacting with the API!')

    @staticmethod
    @weather.exception_catcher
    def _decorator_tester_for_response_error(address):
        """
        Function to test that the decorator does not correctly handle exceptions
        """

        weather.get_weather(address, 'weather')

    def test_assert_decorator_response_error(self):
        """
        checks that the decorator correctly handle
        the incorrect data error

        :return: None
        """

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self._decorator_tester_for_response_error('Londonsd')
        self.assertEqual(fake_out.getvalue().strip(),
                         'Error in API response! \n'
                         'Code: 404 -- city not found')
