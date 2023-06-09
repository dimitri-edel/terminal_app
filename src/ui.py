import os  # import operating system routines
from tabulate import tabulate  # needs pip install tablulate

import datetime
import colorama
from colorama import Fore, Back, Style
from src.api import RequestInfo, RequestParameters
from src.config import Configuration as conf
import src.json_file as jsn

class TextTable:
# The TextTable class uses tabulate to wrap data in a table    
    def __init__(self, rows) -> None:
    # Contructor will create a table with the number of rows 
    # stated in the parameter
        self.rows = rows
        self.current_row = 0        
        self.table = []
        # Create a list with as many rows as stated in the parameter
        for i in range(rows):
            self.table.append([])

    def next_row(self):
        # Used, as an option, for navigating through the rows in a loop
        self.current_row += 1

    def reset_row(self):
        # Used, as an option, for navigating through the rows in a loop
        self.current_row = 0

    def print_forecast(self, response_info, forecast_mode):
        # Print the forecast stored in response_info
        # If the forecast mode is set to 'hourly', then add the first 
        # column with the heading TIME and up to 24 rows like 'hh:00'
        if forecast_mode == "hourly":
            self.__add_hours_columns()
        # Copy the data from response_info
        self.__add_forecast_columns(response_info, forecast_mode)
        # Print the table in green
        print(
            Fore.GREEN
            + Style.BRIGHT
            + tabulate(self.table, headers="firstrow", tablefmt="fancy_grid")
        )
        # Add three lines after the table to add some space separation between it and the next lines
        print("\n\n\n")

    def print_todays_forecast(self, response_info, forecast_mode):
        # Copy the data in response_info and print it inside a table
        # If forecast mode is set to average then show date, average temperature and condition
        if forecast_mode == "average":
            self.reset_row()
            self.table[self.current_row].append(
                f"{response_info.response_table[0]['date']}"
            )
            self.next_row()
            txt_row = f"""{response_info.response_table[0]['avg_temp']}
                {response_info.response_table[0]['condition']}"""""
            dedent_row = "\n".join([m.lstrip() for m in txt_row.split("\n")])
            self.table[self.current_row].append(dedent_row)
            print(
                Fore.GREEN
                + Style.BRIGHT
                + tabulate(self.table, headers="firstrow", tablefmt="fancy_grid")
            )
            return
        # If the forecast mode is set to 'hourly', then the table will only copy the
        # entries starting at the current hour and ignore the ones that preceed them
        # start with the current hour
        start_index = (
            datetime.datetime.now().hour - 1 if datetime.datetime.now().hour > 0 else 0
        )
        # Reset the index of the row within the table
        self.reset_row()
        for i in range(start_index, 24, 1):
            if i == start_index:
                self.table[self.current_row].append("TIME")
            elif i <= 9 and i > 0:
                self.table[self.current_row].append(f"0{self.current_row}:00")
            else:
                self.table[self.current_row].append(f"{i}:00")
            self.next_row()
        # Reset the index of the row within the table
        self.reset_row()
        # Index in the response_table object
        response_table_index = (
            0  # The forecast for today will only contain this one entry
        )
        self.table[self.current_row].append(
            f"DATE: {response_info.response_table[response_table_index]['date']}"
        )
        # Now append the rows with data to the column
        for i in range(start_index, 24, 1):
            data = response_info.response_table[response_table_index]["hourly"][i]
            self.table[self.current_row].append(data)
            # Next row in the table
            self.next_row()
        print(
            Fore.GREEN
            + Style.BRIGHT
            + tabulate(self.table, headers="firstrow", tablefmt="fancy_grid")
        )

    def __add_hours_columns(self):
    # Used for hourly forecast. The method appends the first column to the table
    # The column contains a header that reads TIME and 24 consequitive rows 
    # carring the hour like so hh:00
        for row in range(25):
            if row == 0:
                self.table[row].append("TIME")
            elif row <= 9 and row > 0:
                self.table[row].append("0" + str(row) + ":00")
            else:
                self.table[row].append(str(row) + ":00")

    def __add_forecast_columns(self, response_info, forecast_mode):
    # The method copies the data from response_info.response_table to self.table
    # The self.table property contains the data for the tabulate() function from
    # tabulate library. 
        for response_table_index in range(len(response_info.response_table)):
            # Reset the current_row within the table
            self.reset_row()
            self.table[self.current_row].append(
                str(response_info.response_table[response_table_index]["date"])
            )
            # Go to the next row
            self.next_row()
            if forecast_mode == "hourly":
                for hourly in response_info.response_table[response_table_index][
                    "hourly"
                ]:
                    # Make the column narrower by replacing the first white space with a new line
                    txt_hourly = hourly.replace(" ", "\n", 1)
                    self.table[self.current_row].append(txt_hourly)
                    # Go to the next entry
                    self.next_row()
            else:
                entry_text = f"""{response_info.response_table[response_table_index]['avg_temp']}
                {response_info.response_table[response_table_index]['condition']}"""
                # Remove indentations from the multi line string
                dedent_text = "\n".join([m.lstrip() for m in entry_text.split("\n")])
                self.table[self.current_row].append(dedent_text)
                # Go to the next entry
                self.next_row()


class UserInterface:
    # UserInterface handles input and output on the terminal.
    # It prints tables and messages for the user and gets the commands 
    # issued by the user and evaluates them, then triggers the according
    # response. 
    # Moreover, it harbors the main() method that serves as the starting
    # point for the script.
    def __init__(self) -> None:
        self.EXIT = False
        # Number of days to be convered in the forecast
        self.FORECAST_SPAN = 3
        # Which temperature unit should be displayed
        self.TEMPERATURE_UNIT = "f"
        self.NAME_OF_CITY = "Austin"
        self.FORECAST_MODE = "hourly"

    def __show_current_weather(self):
        # Show the current weather
        # Table that holds the data to be printed
        table = []
        # Parameters for the RequestInfo constructor
        parameters = RequestParameters(number_of_days=1, city=self.NAME_OF_CITY)
        # Create an instance of RequestInfo, which will in turn
        # send a request to the online API
        info = RequestInfo(parameters=parameters)
        # Extract the response, received from the API
        try:
            res = info.get_response(
                self.TEMPERATURE_UNIT,
                forecast_mode=self.FORECAST_MODE,
                forecast_span=self.FORECAST_SPAN,
            )
        # If an error occurs during the transmittion print the error message on the terminal
        except Exception as e:
            print(f"{Fore.RED}{Back.WHITE}{e}")
            return

        curr_temp = str(res.response_table[0]["current_temperature"])
        curr_date = str(res.response_table[0]["date"])
        condition = str(res.response_table[0]["condition"])
        table.append([])
        table[0] = ["CURRENT DATE: ", "CURRENT TEMPERATURE: ", "CONDITION:"]
        table.append([])
        table[1] = [curr_date, curr_temp, condition]
        print(
            Fore.GREEN
            + Style.BRIGHT
            + tabulate(table, headers="firstrow", tablefmt="fancy_grid")
        )
        # Add some extra space after the table to speparate it from next lines
        print("\n\n\n")

    def __print_todays_forecast(self):
        # Print the forecast for the current day
        # Pack the parameters for the RequestInfo Object
        parameters = RequestParameters(number_of_days=1, city=self.NAME_OF_CITY)
        # Instanciate a RequestInfo object
        info = RequestInfo(parameters=parameters)
        # Try and send a HTTP-Request to the server and save its response in a ResponseInfo object named res
        try:
            res = info.get_response(
                self.TEMPERATURE_UNIT,
                forecast_mode=self.FORECAST_MODE,
                forecast_span=self.FORECAST_SPAN,
            )
        # If an error occurs during the transmittion print the error message on the terminal
        except Exception as e:
            print(e)
            return
        # For table with average temperatures use 2 rows
        if self.FORECAST_MODE == "average":
            t = TextTable(2)
            # t.print_forecast(response_info=res, forecast_mode=self.FORECAST_MODE)
            t.print_todays_forecast(response_info=res, forecast_mode=self.FORECAST_MODE)
        # For table with an hourly forecast 25 rows
        else:
            # Number of rows depends on what time it is. 25 - hour , because it includes the current hour
            rows = 25 - datetime.datetime.now().hour
            t = TextTable(rows=rows)
            t.print_todays_forecast(response_info=res, forecast_mode=self.FORECAST_MODE)

    def __print_forecast(self, number_of_days):
        # Prints the forecast
        tables = []
        table_index = 0
        # Assemble the parameter for RequestInfo
        parameters = RequestParameters(
            number_of_days=self.FORECAST_SPAN, city=self.NAME_OF_CITY
        )        
        info = RequestInfo(parameters=parameters)
        # Try and send an HTTP-Request to the API server and if the request is successful
        # store data inside the 'res'-object of TYPE ResponseInfo
        try:
            res = info.get_response(
                self.TEMPERATURE_UNIT,
                forecast_mode=self.FORECAST_MODE,
                forecast_span=self.FORECAST_SPAN,
            )
        # If the Request did not succeed notify the user by printing the error message on terminal
        except Exception as e:
            print(Fore.RED + Back.WHITE + str(e))
            return

        for index in range(len(res.response_table)):
            # assemple the headers of the table
            tables.append([])
            tables[table_index].append(["DATE", res.response_table[index]["date"]])
            if self.FORECAST_MODE == "hourly":
                hour = 0
                for time in res.response_table[index]["hourly"]:
                    str_temp = str(time)
                    str_time = str(hour) + ":00 "
                    # assemple next row of the table
                    tables[table_index].append([str_time, str_temp])
                    # next hour
                    hour += 1
            # next teble
            table_index += 1

        # For table with average temperatures use 2 rows
        if self.FORECAST_MODE == "average":
            t = TextTable(2)
        # For table with an hourly forecast 25 rows
        else:
            t = TextTable(25)
        t.print_forecast(response_info=res, forecast_mode=self.FORECAST_MODE)
    
    def main(self):
        # Main method serves as the starting point for the script
        # Initialize colorama and set it to autoreset upon every print statement
        colorama.init(autoreset=True)
        self.__get_settings()
        # Clear the screen when starting up
        self.__clear_screen()
        # Keep the user in the loop until the exit command is issued
        while self.EXIT is False:
            self.__get_user_input()

    def __get_user_input(self):
        # Prompt user to enter a command
        # And evaluate user's input and execute the command
        self.__print_switchboard()
        print(Fore.GREEN + Style.BRIGHT + Back.BLACK + "Enter command:")
        _input = input()
        if _input.lower() == "exit":
            self.EXIT = True
        elif _input.lower() == "today":
            self.__clear_screen()
            self.__print_todays_forecast()
        elif _input.lower() == "forecast":
            self.__clear_screen()
            self.__print_forecast(self.FORECAST_SPAN)
        elif _input.lower() == "current":
            self.__clear_screen()
            self.__show_current_weather()
        elif _input.lower() == "get settings":
            self.__clear_screen()
            self.__get_settings()
        elif _input.lower() == "set tu":
            self.__clear_screen()
            self.__set_temperature_unit()
        elif _input.lower() == "set fs":
            self.__clear_screen()
            self.__set_forecast_span()
        elif _input.lower() == "city":
            self.__clear_screen()
            self.__set_name_of_city()
        elif _input.lower() == "set fm":
            self.__clear_screen()
            self.set_forecast_mode()
        else:
            # Print an error message if the command has not been found 
            print(Fore.RED + Back.WHITE + f"The command '{_input}' is not defined!")

    # Set the preferred temperature unit
    # User can choose between Fahrenheit and Celcius

    def __set_temperature_unit(self):
        # Prompt the user to enter the temperature unit
        print(
            Fore.GREEN
            + Style.BRIGHT
            + Back.BLACK
            + "Enter temperature unit [ F / C ] :"
        )
        unit = input()
        # If the input was a valid temperature unit then set the change in this object
        # and notify the user about the change
        # If the input was not a valid temperature unit notify the user about the failure
        if unit.lower() == "f" or unit.lower() == "c":
            self.TEMPERATURE_UNIT = unit
            if unit.lower() == "c":
                print(Fore.CYAN + Style.BRIGHT + "Temperature Unit set to Celcius!")
            else:
                print(Fore.CYAN + Style.BRIGHT + "Temperature Unit set to Fahrenheit!")
        else:
            print(
                Fore.RED
                + Back.WHITE
                + "You can only put F for Fahrenheit or C for Celicius!"
            )

    def __set_forecast_span(self):
        # Prompt the user to enter the span of forecast
        print(Fore.GREEN + Style.BRIGHT + Back.BLACK + "Enter number of days: ")
        days = input()        
        setting = 0
        # If user's input is a number and the number is within the allowed range
        # Then update the settings. If the number is outside of the range notify
        # user about it and fall back to a maximum or minimum
        if days.isnumeric():
            if int(days) > 3:
                setting = 3
                print(
                    Fore.RED
                    + Back.WHITE
                    + "Maximum span is 3 days, current setting is now 3 days!"
                )
            elif int(days) < 1:
                setting = 1
                print(
                    Fore.RED
                    + Back.WHITE
                    + "Minimum is 1 day, current setting is now 1 day!"
                )
            else:
                setting = int(days)
            self.FORECAST_SPAN = setting
            self.__update_settings()
            print(f"{Fore.CYAN}{Style.BRIGHT}Forecast span set to {setting} days!")
        else:
            # If the user entered something that is not a number then notify the user
            print(Fore.RED + Back.WHITE + "Number of days must be a number!")

    def __set_name_of_city(self):
        # Prompt the user to enter the name of the sity
        print(Fore.GREEN + Style.BRIGHT + Back.BLACK + "Enter name of city:")
        city = input()
        # Save user's input within this object
        self.NAME_OF_CITY = city.capitalize()
        # Save user's input in the settings file
        self.__update_settings()
        # Notify user about the change
        print(f"{Fore.CYAN}{Style.BRIGHT} Name of city set to {city.capitalize()}")

    def set_forecast_mode(self):
        # Prompt the user to enter the abriviation for the forecast mode they wish to use
        print(
            Fore.GREEN + Style.BRIGHT + Back.BLACK + "Enter forecast mode: [AVG | HLY]?"
        )
        fm = input()
        # If user entered a valid forecast mode, notifiy user about the change
        # If user entered an invalid name, then notifiy user about the mistake
        if fm.lower() == "avg":
            self.FORECAST_MODE = "average"
        elif fm.lower() == "hly":
            self.FORECAST_MODE = "hourly"
        else:
            print(Fore.RED + Back.WHITE + "The only options are : AVG and HLY !")
        print(f"{Fore.CYAN}{Style.BRIGHT}Current forecast mode: {self.FORECAST_MODE}")

    def __update_settings(self):
        # Update settings in the file
        conf().update_settings(
            temp_unit=self.TEMPERATURE_UNIT,
            forecast_span=self.FORECAST_SPAN,
            name_of_city=self.NAME_OF_CITY,
        )
        print("Settings have been updated!")

    
    def __get_settings(self):
        # Read settings from the file
        data = conf().get_settings()
        self.TEMPERATURE_UNIT = data["temperature_unit"]
        self.FORECAST_SPAN = data["forecast_span"]
        self.NAME_OF_CITY = data["name_of_city"]

    def __print_switchboard(self):
        # Print the table with commands and their descritpions
        swtich_board = []
        headers_colors = f"{Back.BLACK}{Fore.YELLOW}{Style.BRIGHT}"
        cell_colors = f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}"
        command_colors = f"{Fore.GREEN}{Style.BRIGHT}{Back.BLACK}"        
        swtich_board.append(
            [
                f"{headers_colors}DESCRIPTION{cell_colors}",
                f"{headers_colors}COMMAND{cell_colors}",
            ]
        )
        # description string of the forecast command
        desc_forecast = """Show the forcast for the number of days,
        defined in the settings.Default is 3 days,
        and temperature unit defaults to Fahreinheit!"""
        # remove indentations from the multiline string
        dedent_forecast = "\n".join([m.lstrip() for m in desc_forecast.split("\n")])
        swtich_board.append([dedent_forecast, f"{command_colors}forecast{cell_colors}"])
        swtich_board.append(
            ["Show the forcast for today", f"{command_colors}today{cell_colors}"]
        )
        swtich_board.append(
            ["Current weather", f"{command_colors}current{cell_colors}"]
        )
        swtich_board.append(
            [
                "Set the temperature unit[Celcius/Fahrenheit]",
                f"{command_colors}set tu{cell_colors}",
            ]
        )
        # description of the set temerature unit command
        desc_tu = """Set the span of a forecast.
        How many days to cover?
        Maximum is 3!"""
        # remove indentations from the multiline string
        dedent_tu = "\n".join([m.lstrip() for m in desc_tu.split("\n")])
        swtich_board.append([dedent_tu, f"{command_colors}set fs{cell_colors}"])
        # description of the set forecast mode command
        desc_fm = """Set forecast mode. It lets you choose between hourly
        and average temperatures. If set to hourly,
        forecast for every hour of each day will
        be displayed. If set to average, forecast
        will only display the average temperature
        of each day."""
        # remove indentations from the multiline string
        dedent_fm = "\n".join([m.lstrip() for m in desc_fm.split("\n")])
        swtich_board.append([dedent_fm, f"{command_colors}set fm{cell_colors}"])
        # description of the city command
        desc_city = """Set name of the city for for which you want
        the forecast to be. If not set, the setting
        defaults to 'Austin, TX, USA'."""
        # remove indentations from the multiline string
        dedent_city = "\n".join([m.lstrip() for m in desc_city.split("\n")])
        swtich_board.append([dedent_city, f"{command_colors}city{cell_colors}"])
        swtich_board.append(["Exit", f"{command_colors}exit{cell_colors}"])        
        print(cell_colors + tabulate(swtich_board, headers="firstrow", tablefmt="grid"))

    def __clear_screen(self):
        # Clear the screen on the terminal
        os.system("cls" if os.name == "nt" else "clear")
