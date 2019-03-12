"""Module containing functions for working with the http://api.openweathermap.org service API (with GUI)"""

from datetime import datetime
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from supertool import weather, \
    geo_nominatim, definitions as df
from supertool import usefull_widget_tools as uwt

FORECAST_LENGTH = 9
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def from_ts_to_time_of_day(ts) -> str:
    """
    Converts time from timestamp format to string

    :param ts: time
    :return: time as str
    """
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%I%p").lstrip("0")


def set_weather_icon(name):
    """
    Opens a picture by name.

    :param name: picture name
    :return: QPixmap -- picture
    """
    return QtGui.QPixmap(os.path.join(ROOT_PATH, 'weather_images', f"{name}.png"))


class WorkerSignals(QtCore.QObject):
    """Signals for communicating the control flow and the internal worker."""

    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    result = QtCore.pyqtSignal(dict, dict, dict)


class GetWeatherWorker(QtCore.QRunnable):
    """Worker thread for getting weather."""

    signals = WorkerSignals()

    def __init__(self, address):
        """Init GetWeatherWorker"""
        super(GetWeatherWorker, self).__init__()
        self.address = address

    def search(self):
        """
        Requests the coordinates of the addressed address, then asks for the coordinates.

        :return: Returns the weather, forecast and description
        of the place found
        """
        location = geo_nominatim.get_coordinates(self.address)
        description = weather.get_weather(location['coordinates'], 'weather', format_as_json=True)
        forecast = weather.get_weather(location['coordinates'], 'forecast', format_as_json=True)
        return description, forecast, location

    @QtCore.pyqtSlot()
    def run(self):
        """Main method within the workflow."""
        try:
            description, forecast, location = self.search()
        except ValueError as e:
            self.signals.error.emit(f'Error in the entered data! \n{e}')
        except (df.ResponseError, KeyError) as e:
            self.signals.error.emit(f'Error in API response! \n{e}')
        except df.ProcessError as e:
            self.signals.error.emit(f'Error in the process of interacting with the API! \n{e}')
        except Exception as e:
            self.signals.error.emit(f'Error! {e}')
        else:
            self.signals.result.emit(description, forecast, location)
        finally:
            self.signals.finished.emit()


class WeatherWidget(QtWidgets.QWidget):
    """Widget showing the current weather."""

    def __init__(self, parent=None):
        """Inti WeatherWidget"""
        super(WeatherWidget, self).__init__(parent)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("weather_gridLayout")

        self.description_img = QtWidgets.QLabel(self)

        self.description = QtWidgets.QLabel(self)
        self.temperature_value = QtWidgets.QLabel(self)

        self.wind_speed = QtWidgets.QLabel(self)
        self.wind_speed.setText('Wind speed')
        self.wind_speed_value = QtWidgets.QLabel(self)

        self.humidity = QtWidgets.QLabel(self)
        self.humidity.setText('Humidity')
        self.humidity_value = QtWidgets.QLabel(self)

        self.pressure = QtWidgets.QLabel(self)
        self.pressure.setText('Pressure')
        self.pressure_value = QtWidgets.QLabel(self)

        self.cloudiness = QtWidgets.QLabel(self)
        self.cloudiness.setText('Cloudiness')
        self.cloudiness_value = QtWidgets.QLabel(self)

        self.gridLayout.addWidget(self.description_img, 0, 0, 2, 1)

        self.gridLayout.addWidget(self.description, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.wind_speed, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.humidity, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.pressure, 0, 4, 1, 1)
        self.gridLayout.addWidget(self.cloudiness, 0, 5, 1, 1)

        self.gridLayout.addWidget(self.temperature_value, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.wind_speed_value, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.humidity_value, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.pressure_value, 1, 4, 1, 1)
        self.gridLayout.addWidget(self.cloudiness_value, 1, 5, 1, 1)


class GetWeatherWidget(QtWidgets.QWidget):
    """Main Get Weather widget."""

    def __init__(self, parent=None):
        """Init GetWeatherWidget"""
        super(GetWeatherWidget, self).__init__(parent)
        self.title = 'Weather GUI'

        # make some beauty
        self.set_style()

        self.data_layout = QtWidgets.QVBoxLayout(self)
        self.line_edit_with_buttons = uwt.LineEditWithBottoms('Введите адрес', self)
        self.first_start = True
        self.thread_pool = QtCore.QThreadPool(self)

        self.setGeometry(QtCore.QRect(100, 100, 600, 230))
        self.data_layout.setObjectName("data_layout")

        self.setWindowTitle(self.title)

        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Minimum)

        button = uwt.create_button('starter', 'Search',
                                   self.line_edit_with_buttons,
                                   font, size_policy)

        # interaction logic
        button.clicked.connect(self.search_button_pressed)
        self.line_edit_with_buttons.add_button(button)

        self.line_edit_with_buttons.set_font(font)

        self.forecast_widget = QtWidgets.QWidget(self)
        self.forecast_labels = []

        self.gridLayout = QtWidgets.QGridLayout(self.forecast_widget)
        self.gridLayout.setObjectName("gridLayout")

        for i in range(FORECAST_LENGTH):
            fields = {
                'time': QtWidgets.QLabel(self),
                'img': QtWidgets.QLabel(self),
                'temperature': QtWidgets.QLabel(self)
            }
            for num, value in enumerate(fields.values()):
                self.gridLayout.addWidget(value, num, i, 1, 1)

            self.forecast_labels.append(fields)

        self.top_spacer = QtWidgets.QSpacerItem(20, 40,
                                                QtWidgets.QSizePolicy.Minimum,
                                                QtWidgets.QSizePolicy.Expanding)
        self.bot_spacer = QtWidgets.QSpacerItem(20, 40,
                                                QtWidgets.QSizePolicy.Minimum,
                                                QtWidgets.QSizePolicy.Expanding)

        self.data_layout.addItem(self.top_spacer)
        self.data_layout.addWidget(self.line_edit_with_buttons)

        self.infoWidget = QtWidgets.QWidget(self)
        self.info_layout = QtWidgets.QHBoxLayout(self.infoWidget)

        self.current_weather_widget = WeatherWidget(self.infoWidget)

        self.address_label = QtWidgets.QLabel(self.infoWidget)
        self.address_label.setWordWrap(True)
        self.info_layout.addWidget(self.current_weather_widget)
        self.data_layout.addWidget(self.address_label)

        self.data_layout.addWidget(self.infoWidget)
        self.data_layout.addWidget(self.forecast_widget)
        self.data_layout.addItem(self.bot_spacer)

        self.infoWidget.hide()
        self.forecast_widget.hide()

    def keyPressEvent(self, event):  # noqa
        """Starts a weather searching when you press enter."""
        if event.key() == 16777220:
            self.search_button_pressed()

    def alert(self, message):
        """
        Error processing

        :param message: error message
        :return:
        """
        self.address_label.setText(message)
        self.infoWidget.hide()
        self.forecast_widget.hide()

    def search_button_pressed(self):
        """Start the search: create a new search instans, send it to the thread and connect signals to the handlers."""
        worker = GetWeatherWorker(self.line_edit_with_buttons.get_text())
        worker.signals.result.connect(self.weather_result)
        worker.signals.error.connect(self.alert)
        self.thread_pool.start(worker)

    def weather_result(self, description, forecasts, location):
        """
        Processing of weather query results.

        :param description: description of the current weather
        :param forecasts: description of the weather forecast
        :param location: location found
        :return: None
        """
        for n, forecast in enumerate(forecasts['list'][:FORECAST_LENGTH]):
            self.forecast_labels[n]['time'].setText(from_ts_to_time_of_day(forecast['dt']))
            self.forecast_labels[n]['temperature'].setText(f"{forecast['main']['temp']} °C")
            self.forecast_labels[n]['img'].setPixmap(set_weather_icon(forecast['weather'][0]['icon']))

        self.address_label.setText(location['name'])

        if self.first_start:
            self.data_layout.removeItem(self.top_spacer)
            self.first_start = False

        self.current_weather_widget.description.setText(description['weather'][0]['description'])
        self.current_weather_widget.description_img.setPixmap(set_weather_icon(description['weather'][0]['icon']))
        self.current_weather_widget.temperature_value.setText(f"{description['main']['temp']} °C")
        self.current_weather_widget.wind_speed_value.setText(f"{description['wind']['speed']} m/s")
        self.current_weather_widget.humidity_value.setText(f"{description['clouds']['all']} %")
        self.current_weather_widget.pressure_value.setText(f"{description['main']['pressure']} hPa")
        self.current_weather_widget.cloudiness_value.setText(f"{description['main']['humidity']} %")
        self.infoWidget.show()
        self.forecast_widget.show()

    def set_style(self):
        """Optional method for setting dark them"""
        self.setStyleSheet("""
                QWidget { background-color: #3C3F41 }

                .QLabel {
                    color: #C1C1C1;
                    background-color: #3C3F41;
                    selection-color: #C1C1C1;
                    selection-background-color: #545555;
                    font: 10pt "Monaco";
                    }


                .QLineEdit {
                    color: #C1C1C1;
                    background-color: #3C3F41;
                    selection-color: #92BD6C;
                    selection-background-color: #545555;
                    border: 1px solid #313335;
                    font: 15pt "Monaco";
                    }

                QPushButton {
                    background-color: #3C3F41;
                    color: #C1C1C1;
                    border: 1px solid #313335;
                    padding: 1px;
                    min-width: 80px;
                    text-align: center;
                    font: 14pt "Monaco";
                }

                QPushButton:hover  {
                    color: #C1C1C1;
                    border: 2px solid #92BD6C;
                    padding: 1px;
                    min-width: 80px;
                }

                QPushButton:pressed{
                    color: #92BD6C;
                    border: 2px solid #92BD6C;
                    padding: 1px;
                    min-width: 80px;
                }

                """)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GetWeatherWidget()
    window.show()
    sys.exit(app.exec_())
