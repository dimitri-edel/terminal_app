from datetime import date
import requests  # needs pip install requests

""" RequestParmaters - An instance of this class is used for passing
    parameters to RequestInfo constructor
"""


class RequestParameters:
    def __init__(self, number_of_days, city) -> None:
        self.number_of_days = number_of_days
        self.city = city


"""
    RequestInfo
    DESCRIPTIOIN: Helps creating and sending HTTP-Requests to the API 
"""


class RequestInfo:
    def __init__(self, parameters) -> None:
        if not isinstance(parameters, RequestParameters):
            return None
        self.API_KEY = "?key=288ee8558204498d9cf04212230604"
        self.QUERY = "&q=" + parameters.city
        self.FORECAST_SPAN = "&days=" + str(parameters.number_of_days)
        self.BASE_URL = "http://api.weatherapi.com/v1/forecast.json"
        self.CURL = self.BASE_URL + self.API_KEY + self.QUERY + self.FORECAST_SPAN
        # x = requests.get('https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m')

    """ Get Response from API and assemble a ResponseInfo object and return it
    PARAMETER: temperature_unit
    VALUES : 'f' for Fahrehneit or 'c' for Celcius
    Deliver Fahrenheit or Celcius Readings
    PARAMETER: forecast_mode
    VALUES: 'hourly' will deliver a table with anticipated temperatures for each hour of the day
            'average' will only diliver the anticipated average temperatures, humidity, etc., for each day
    RETURN: Object of type ResponseInfo, which contains a map, that is retrieved from
    a JSON-file. The map contains all the weather-data received from the API
    """

    def get_response(self, temperature_unit, forecast_mode, forecast_span):
        response = ResponseInfo()
        x = requests.get(self.CURL)
        json_obj = x.json()
        # Day index in the response.response_table list
        # day = 0
        # If the response returns an error, then raise an exception
        if "error" in json_obj:
            additional_text = f"""\nYou might have misspelled the name of the city, 
            or the city is not covered! 
            Requested city name was {self.QUERY}"""

            dedent_text = "\n".join([m.lstrip() for m in additional_text.split("\n")])
            raise Exception(json_obj["error"]["message"] + dedent_text)

        # Extract information from the dictionary named 'current' and put it in response objec
        self.__extract_current_weather(json_obj, response, temperature_unit)
        # Find dictionary named 'forecastday', and copy relevant data to response.response_table
        # The 'forecastday' dictionary is nested inside the second level of a multidimensional dictionary
        # First level contains three objects in total: 'location', 'current', 'forecast'

        self.__extract_forecast(json_obj, response, forecast_mode, temperature_unit, forecast_span)

        return response

    def __extract_current_weather(self, json_obj, response, temperature_unit):
        # The index of the first list in response.response_table. It always contains
        # information on the current day
        current_day_index = 0
        if temperature_unit == "f":
            current_temperature = f"{json_obj['current']['temp_f']}°F"
        else:
            current_temperature = f"{json_obj['current']['temp_c']}°C"
        response.response_table[current_day_index][
            "current_temperature"
        ] = current_temperature
        response.response_table[current_day_index]["date"] = self.__extract_date(
            json_obj["location"]["localtime"]
        )
        response.response_table[current_day_index]["condition"] = json_obj["current"]["condition"]["text"]

    def __extract_forecast(self, json_obj, response, forecast_mode, temperature_unit, forecast_span):
        # Day index is used for
        day_index = 0
        for day_info in json_obj["forecast"]["forecastday"]:
            # The date for the first day has already been added by __extract_current_weather(),
            # to the first element, so skip the first entry
            if day_index > 0:
                # Extract date from the timestamp in the json_obj
                date = self.__extract_date(day_info["date"])
                # add date of the current element to response
                response.response_table[day_index]["date"] = date
                # If the forecast_mode is set to 'average', then copy relevant data
                # to response.response_table and skip the hourly forecast
            if forecast_mode == "average":
                # Weather condition text                
                condition = day_info["day"]["condition"]["text"]
                # avaerage temperature
                avg_temp = (
                    day_info["day"]["avgtemp_c"]
                    if temperature_unit == "c"
                    else day_info["day"]["avgtemp_f"]
                )
                response.response_table[day_index][
                    "avg_temp"
                ] = f"{avg_temp}°{temperature_unit.upper()}"
                response.response_table[day_index]["condition"] = condition
                # Increment the current element index
                day_index += 1
                # If the day_index exceepds the number of days required by the forecast span
                if day_index >= forecast_span:
                    break
                else:
                    # Add another dictionary to the list in the response
                    response.next_day()
                    continue

            # add hourly report for the current element to respoonse
            self.__extract_hourly_forecast(
                response, temperature_unit, day_index, day_info
            )
            # Increment the current element index
            day_index += 1
            # If the day_index exceepds the number of days required by the forecast span
            if day_index >= forecast_span:
                break
            else:
                # Add another dictionary to the list in the response
                response.next_day()

    def __extract_hourly_forecast(self, response, temperature_unit, day_index, day_info):
        # Sometimes the api delivers further hours for the night time, in which case the number of
        # entries in the hourly list exceeds 24 entries.
        # hourly_count counts the number of entries and is used to ensure that only 24 entries are
        # attached to the response.response_table object. Otherwise it will result in an ERROR.
        hourly_count = 0
        for hourly in day_info["hour"]:
            hourly_count += 1
            # Sometimes the api delivers further hours for the night time, in which case the number of
            # entries in the hourly list exceeds 24 entries. The next instruction makes sure, that in
            # that case those entries are not attached to the response object.
            if hourly_count > 24:
                break
            if temperature_unit == "f":
                response.response_table[day_index]["hourly"].append(
                    f"{hourly['temp_f']}°{temperature_unit.upper()} {hourly['condition']['text']}"
                )
            else:
                response.response_table[day_index]["hourly"].append(
                    f"{hourly['temp_c']}°{temperature_unit.upper()} {hourly['condition']['text']}"
                )

    def __extract_date(self, timestamp):
        """Extracts the date from a timestamp


        Args:
            timestamp (string):The string is formatted like so: "2024/04/01 14:00:00:00"

        Returns:
            string: The date extracted from the timestamp, which will look like this: "Mon.1.Apr"
        """
        data = timestamp.split(" ")
        data_split = data[0].split("-")
        data_year = int(data_split[0])
        data_month = int(data_split[1])
        data_day = int(data_split[2])
        date_obj = date(data_year, data_month, data_day)
        date_as_str = ""
        data_weekday = self.__get_name_of_weekday(date_obj)
        date_as_str = (
            data_weekday + " " + str(data_day) + "." + self.__get_name_of_month(data_month - 1)
        )

        return date_as_str

    def __get_name_of_weekday(self, date):
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return weekdays[date.weekday()]

    def __get_name_of_month(self, month_as_int):
        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        return months[month_as_int]


class ResponseInfo:
    def __init__(self) -> None:
        current_day = {
            "current_temperature": "",
            "avg_temp": "",
            "condition": "",
            "humidity": "",
            "date": "",
            "hourly": [],
        }
        self.response_table = []
        self.response_table.append(current_day)

    def next_day(self):
        next_row = {"date": "", "avg_temp": "", "condition": "", "hourly": []}
        self.response_table.append(next_row)
