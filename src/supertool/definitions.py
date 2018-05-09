NOMINATIM_URL = "http://nominatim.openstreetmap.org"
NOMINATIM_DEFAULT_POSTFIX = '/search'

OPEN_WEATHER_API_KEY = 'c8d657d3595e266e5a04cfe2f7282567'
OPEN_WEATHER_URL = "http://api.openweathermap.org/data/2.5/"
REPORT_TABLE_SIZE = 50


class ResponseError(Exception):
    pass


class ProcessError(Exception):
    pass
