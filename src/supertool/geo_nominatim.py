"""Module containing functions for working with the http://nominatim.openstreetmap.org service API"""
import requests

from supertool import definitions as df


def make_nominatim_request(address: str,
                           request_postfix: str = df.NOMINATIM_DEFAULT_POSTFIX,
                           url: str = df.NOMINATIM_URL) -> 'requests.models.Response':
    """
    Sends a request to http://nominatim.openstreetmap.org and returns a response

    :param address: address for which we want
    to know the coordinates
    :param request_postfix: api service of
    http://nominatim.openstreetmap.org
    :param url: url for request
    :return: 'Response' -- json response
    """
    query_params = {
        "q": address,
        "format": "json"
    }

    try:
        response = requests.get(url + request_postfix,
                                params=query_params)
    except requests.exceptions.RequestException as e:
        raise df.ProcessError(f'Server interacting error: {e}')
    return response


def get_coordinates(address: str) -> dict:
    """
    Requests from http://nominatim.openstreetmap.org the coordinates corresponding to the given address

    :param address: address passed in the request
    :return: A dictionary that contains a description
    of the place that corresponds to the address,
    its latitude and longitude
    """
    response = make_nominatim_request(address).json()

    if not response:
        raise ValueError(f"Incorrect address: {address}")

    return {
        'name': response[0]['display_name'],
        'coordinates': {
            'lat': response[0]['lat'],
            'lon': response[0]['lon']
        }
    }


if __name__ == '__main__':  # pragma: no cover
    pass
