import json
import os
from src.api import ResponseInfo
from datetime import date


class JsonFile:
    def __init__(self) -> None:
        self.aDict = {}

    def openFile(self, name):
        file_content = ""
        path = os.path.normcase(f"./conf/{name}")
        f = open(path, "r")
        file_content = f.read()
        f.close()
        return file_content

    def printJson(self, content):
        self.aDict = json.loads(content)
        print(self.aDict)

    def test(self):
        content = self.openFile("json_obj.json")
        json_obj = json.loads(content)
        response = ResponseInfo()
        forecast_mode = "hourly"
        temperature_unit = "f"
        day = 0

        # Extract information from the dictionary named 'current' and put it in response objec
        self.extract_current_weather(json_obj, response, temperature_unit)
        # Find dictionary named 'forecastday', and copy relevant data to response.response_table
        # The 'forecastday' dictionary is nested inside the second level of a multidimensional dictionary
        # First level contains three objects in total: 'location', 'current', 'forecast'
        
        self.extract_forecast(json_obj, response, forecast_mode, temperature_unit)

        return response

    def extract_current_weather(self, json_obj, response, temperature_unit):
        # The index of the first list in response.response_table. It always contains
        # information on the current day
        current_day_index = 0
        if temperature_unit == 'f':
            current_temperature = f"{json_obj['current']['temp_f']}°F"
        else:
            current_temperature = f"{json_obj['current']['temp_c']}°C"
        response.response_table[current_day_index]['current_temperature'] = current_temperature
        response.response_table[current_day_index]['date']\
            = self.extract_date(json_obj['location']['localtime'])

    def extract_forecast(self, json_obj, response, forecast_mode, temperature_unit):
        # Day index is used for 
        day_index = 0
        for day_info in json_obj['forecast']['forecastday']:
            # The date for the first day has already been added by extract_current_weather(),
            # to the first element, so skip the first entry
            if day_index > 0:
                            # Extract date from the timestamp in the json_obj
                date = self.extract_date(day_info["date"])
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
                # Add another dictionary to the list in the response
                response.nextDay()
                continue
            
            
            # add hourly report for the current element to respoonse
            self.extract_hourly_forecast(response, temperature_unit, day_index, day_info)
            # Increment the current element index
            day_index += 1
            # Add another dictionary to the list in the response
            response.nextDay()

    def extract_hourly_forecast(self, response, temperature_unit, day_index, day_info):
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

    def extract_date(self, timestamp):
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
        data_weekday = self.getWeekdayName(date_obj)
        date_as_str = (
            data_weekday + " " + str(data_day) + "." + self.getMonthName(data_month - 1)
        )

        return date_as_str

    def getWeekdayName(self, date):
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return weekdays[date.weekday()]

    def getMonthName(self, month_as_int):
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
