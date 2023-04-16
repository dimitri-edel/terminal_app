from datetime import date
import requests  # needs pip install requests

''' RequestParmaters - An instance of this class is used for passing
    parameters to RequestInfo constructor
'''


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
        self.CURL = self.BASE_URL + self.API_KEY + self.QUERY \
            + self.FORECAST_SPAN
        # x = requests.get('https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m')

    ''' Get Response from API and assemble a ResponseInfo object and return it
    PARAMETER: temperature_unit
    VALUES : 'f' for Fahrehneit or 'c' for Celcius
    Deliver Fahrenheit or Celcius Readings
    PARAMETER: forecast_mode
    VALUES: 'hourly' will deliver a table with anticipated temperatures for each hour of the day
            'average' will only diliver the anticipated average temperatures, humidity, etc., for each day
    RETURN: Object of type ResponseInfo, which contains a map, that is retrieved from
    a JSON-file. The map contains all the weather-data received from the API
    '''

    def getRespoonse(self, temperature_unit, forecast_mode):
        day = 0
        response = ResponseInfo()
        x = requests.get(self.CURL)
        json_obj = x.json()
        # If the response returns an error, then raise an exception
        if "error" in json_obj:
            additional_text = "You might have misspelled the name of the city, or the city is not covered!"            
            raise Exception(json_obj["error"]["message"] + additional_text)

        """ Current readings are inside a dictionary named 'current'. Attach current readings
            to the first row in response.response_table
        """
        if temperature_unit == 'f':
            current_temperature = f"{json_obj['current']['temp_f']}°F"
        else:
            current_temperature = f"{json_obj['current']['temp_c']}°C"
        response.response_table[day]['current_temperature'] = current_temperature
        response.response_table[day]['date']\
            = self.extract_date(json_obj['location']['localtime'])
        
        # Find dictionary named 'forecastday', and copy relevant data to response.response_table
        for first_layer in json_obj:
            for second_layer in json_obj[first_layer]:
                if second_layer == 'forecastday':
                    for day_info in json_obj[first_layer][second_layer]:
                        # The date has already been added to the first element
                        # before the loop, so skip the first entry
                        if day > 0:
                            # Extract date from the timestamp in the json_obj
                            date = self.extract_date(day_info['date'])
                            # add date of the current element to response
                            response.response_table[day]['date'] = date
                        # If the forecast_mode is set to 'average', then copy relevant data
                        # to response.response_table and skip the hourly forecast
                        if forecast_mode == 'average':
                            # Weather condition text
                            condition = day_info['day']['condition']['text']
                            # avaerage temperature
                            avg_temp = day_info['day']['avgtemp_c'] if temperature_unit == 'c' else day_info['day']['avgtemp_f']
                            response.response_table[day]['avg_temp'] = f"{avg_temp}°{temperature_unit.upper()}"
                            response.response_table[day]['condition'] = condition  
                           # Increment the current element index
                            day += 1
                            # Add another dictionary to the list in the response
                            response.nextDay()
                            continue
                        hourly_count = 0
                        # add hourly report for the current element to respoonse
                        for hourly in day_info['hour']:
                            hourly_count += 1
                            # Sometimes the api delivers further hours for the night time, which makes no sense
                            # because the same data is in the next days data, but the API started doing that today
                            # So, I need to make sure that the table has a consistent length, or else it will result
                            # in an ERROR
                            if hourly_count > 24:                                
                                continue                            
                            if temperature_unit == 'f':
                                response.response_table[
                                    day]['hourly'].append(f"{hourly['temp_f']}°{temperature_unit.upper()} {hourly['condition']['text']}")
                            else:
                                response.response_table[
                                    day]['hourly'].append(f"{hourly['temp_c']}°{temperature_unit.upper()} {hourly['condition']['text']}")
                        # Increment the current element index
                        day += 1
                        # Add another dictionary to the list in the response
                        response.nextDay()                        
        return response

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
        date_as_str = data_weekday + " " + str(data_day) + "."\
            + self.getMonthName(data_month-1)

        return date_as_str

    def getWeekdayName(self, date):
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return weekdays[date.weekday()]

    def getMonthName(self, month_as_int):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return months[month_as_int]


class ResponseInfo:
    def __init__(self) -> None:
        current_day = {'current_temperature': '', 'avg_temp': '', 'condition' : '', 'humidity': '',  'date': '', 'hourly': []}
        self.response_table = []
        self.response_table.append(current_day)

    def nextDay(self):
        next_row = {'date': '', 'avg_temp': '', 'condition': '', 'hourly': []}
        self.response_table.append(next_row)
