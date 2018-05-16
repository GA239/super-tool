"""
Module containing functions for working with the
http://api.openweathermap.org service API
"""
import functools
import requests
import logging
import typing

from supertool import definitions as df


def make_open_weather_request(location: str or dict,
                              request_postfix: str,
                              url: str = df.OPEN_WEATHER_URL,
                              api_key: str = df.OPEN_WEATHER_API_KEY) -> 'requests.models.Response':
    """
    Sends a request to http://api.openweathermap.org
    and returns a response

    :param location: location query param for openweathermap
    :param request_postfix: api service of openweathermap
    :param url: url for request
    :param api_key: api key for api.openweathermap.org
    :return: 'Response' -- json response
    """

    if isinstance(location, str):
        query_params = {
            'q': location,
        }
    elif isinstance(location, dict):
        try:
            query_params = {
                "lat": location["lat"],
                "lon": location["lon"],
            }
        except KeyError:
            raise ValueError(f"Wrong cords: {location}!")
    else:
        raise TypeError(f"Wrong location: {location}!")

    query_params['appid'] = api_key
    query_params['units'] = 'metric'

    try:
        response = requests.get(url + request_postfix,
                                params=query_params)
    except requests.exceptions.RequestException as e:
        raise df.ProcessError(f'Server interacting error: {e}')
    return response


def get_weather(location: str or dict,
                request_postfix: str,
                format_as_json=False,
                api_key: str = df.OPEN_WEATHER_API_KEY) -> tuple:
    """
    Requests a weather description for a given location

    :param location: location query param for openweathermap
    :param request_postfix: api service of openweathermap ex :
    'weather' for current weather or
    'forecast' for forecast weather
    :param format_as_json: method of presenting the result
    :param api_key: api key for api.openweathermap.org
    :return: List with dates and weather descriptions
    """

    response = make_open_weather_request(location, request_postfix, api_key=api_key)
    response_as_json = response.json()
    if not response.ok:
        raise df.ResponseError(' -- '.join([f"Code: {response_as_json['cod']}",
                                            f"{response_as_json['message']}"]))
    if format_as_json:
        return response_as_json
    return open_weather_reporter(request_postfix)(response_as_json)


def weather_block_report(weather_json_block: dict) -> str:
    """
    Generates a weather report using the information from json

    :param weather_json_block: dictionary with weather information
    :return: str -- report with weather information
    """

    labels = [
        'Description',
        'temperature (Celsius):',
        'pressure (hPa):',
        'humidity (%):',
        'wind speed (meter/sec):',
        'cloudiness (%):'
    ]

    # this is necessary for leveling
    rjust_sizes = [df.REPORT_TABLE_SIZE - len(x) for x in labels]

    values = [
        weather_json_block['weather'][0]['description'],
        weather_json_block['main']['temp'],
        weather_json_block['main']['pressure'],
        weather_json_block['main']['humidity'],
        weather_json_block['wind']['speed'],
        weather_json_block['clouds']['all']
    ]

    report_lines = tuple(zip(labels, values, rjust_sizes))
    return '\n'.join([val[0] + str(val[1]).rjust(val[2])
                      for val in report_lines])


def make_location_report(place: str,
                         country: str,
                         report_prefix: str) -> str:
    """
    Generates a location report using the information from json.
    This report is used as a header for the weather report.

    :param place: the place where the weather was measured
    :param country: the country where the weather was measured
    :param report_prefix: type of weather report,
    current or forecast
    :return: str -- report with location information
    """

    return '\n'.join([
        ''.rjust(df.REPORT_TABLE_SIZE, '-'),
        f'{report_prefix} in {place} ({country})'.center(df.REPORT_TABLE_SIZE),
        ''.rjust(df.REPORT_TABLE_SIZE, '-')
    ])


def current_weather_json_parser(response_as_json: dict) -> tuple:
    """
    Parse the response from the http://api.openweathermap.org
    after requesting the current weather 
    and create the corresponding reports

    :param response_as_json: json response 
    from http://api.openweathermap.org
    :return: tuple -- reports with location 
    and current weather information
    """

    location_report = make_location_report(response_as_json['name'],
                                           response_as_json['sys']['country'],
                                           'Current weather')
    return location_report, weather_block_report(response_as_json)


def forecast_weather_json_parser(response_as_json: dict) -> tuple:
    """
    Parse the response from the http://api.openweathermap.org
    after requesting the forecast weather 
    and create the corresponding reports

    :param response_as_json: json response 
    from http://api.openweathermap.org
    :return: tuple -- reports with location 
    and forecast weather information
    """

    location_report = make_location_report(response_as_json['city']['name'],
                                           response_as_json['city']['country'],
                                           'The weather forecast')

    weather_reports = tuple('\n'.join([block['dt_txt'].center(df.REPORT_TABLE_SIZE),
                                       weather_block_report(block)])
                            for block in response_as_json['list'])

    return location_report, '\n'.join(weather_reports)


def open_weather_reporter(request_postfix: str) -> typing.Callable:
    """
    Returns a function that will parse json from http://api.openweathermap.org
    and will create correct report depending on the service

    :param request_postfix: api service of openweathermap
    :return: typing.Callable -- function that will
    parse json and create report
    """

    if request_postfix == 'forecast':
        return forecast_weather_json_parser
    elif request_postfix == 'weather':
        return current_weather_json_parser
    raise ValueError(f'Reporter for {request_postfix} does not fount!')


def exception_catcher(fn: typing.Callable) -> typing.Callable:
    """
    Decorator, which catches and processes some exceptions
    that may  occur in the current module
    """

    @functools.wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            print(f'Error in the entered data! \n{e}')
        except (df.ResponseError, KeyError) as e:
            print(f'Error in API response! \n{e}')
        except df.ProcessError as e:
            print(f'Error in the process of interacting with the API! \n{e}')
        except Exception as e:  # pragma: no cover
            print(f'Error! {e}')
            logging.exception(e)
    return inner


if __name__ == '__main__':  # pragma: no cover
    pass
