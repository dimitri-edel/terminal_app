import os  # import operating system routines
from tabulate import tabulate  # needs pip install tablulate

import datetime
from src.api import RequestInfo, RequestParameters
from src.config import Configuration as conf


class TextTable:
    def __init__(self, rows) -> None:
        self.rows = rows
        self.current_row = 0
        self.current_column = 0
        self.table = []
        for i in range(rows):
            self.table.append([])

    def next_row(self):
        self.current_row += 1

    def next_column(self):
        self.current_column += 1

    def reset_column(self):
        self.current_column = 0

    def reset_row(self):
        self.current_row = 0
    
    def add_header(self, column_index, text):
        pass

    def add_cell_to_column(self, column_index, text):
        pass

    def addCellToRow(self, text):
        pass

    def printTable(self):
        # Headings
        print(
            chr(0x2554)
            + chr(0x2550) * 20
            + chr(0x2566)
            + chr(0x2550) * 20
            + chr(0x2557)
        )
        print(chr(0x2551) + " " * 20 + chr(0x2551) + " " * 20 + chr(0x2551))
        print(
            chr(0x255A)
            + chr(0x2550) * 20
            + chr(0x2569)
            + chr(0x2550) * 20
            + chr(0x255D)
        )
        # Cells
        print(
            chr(0x250C)
            + chr(0x2500) * 20
            + chr(0x252C)
            + chr(0x2500) * 20
            + chr(0x2510)
        )
        print(chr(0x2502) + " " * 20 + chr(0x2502) + " " * 20 + chr(0x2502))
        print(
            chr(0x2514)
            + chr(0x2500) * 20
            + chr(0x2534)
            + chr(0x2500) * 20
            + chr(0x2518)
        )

        table = [["col1", "col2"], [1, 2], [3, 4]]
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

    def printForcast(self, response_info, forecast_mode):
        if forecast_mode == "hourly":
            self.addHoursColumn()
        self.addForecastColumns(response_info, forecast_mode)
        print(tabulate(self.table, headers="firstrow", tablefmt="fancy_grid"))

    def printTodaysForecast(self, response_info, forecast_mode):
        # start with the current hour
        start_index = datetime.datetime.now().hour - 1 if datetime.datetime.now().hour > 0 else 0
        # This is the index of the row within the table
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
        response_table_index = 0 # The forecast for today will only contain this one entry
        self.table[self.current_row].append(f"DATE: {response_info.response_table[response_table_index]['date']}")
        # Now append the rows with data to the column
        for i in range(start_index, 24, 1):
           data =  response_info.response_table[response_table_index]["hourly"][i]
           self.table[self.current_row].append(data)
           # Next row in the table
           self.next_row()
        print(tabulate(self.table, headers="firstrow", tablefmt="fancy_grid"))

    def addHoursColumn(self):
        for row in range(25):
            if row == 0:
                self.table[row].append("TIME")
            elif row <= 9 and row > 0:
                self.table[row].append("0" + str(row) + ":00")
            else:
                self.table[row].append(str(row) + ":00")

    def addForecastColumns(self, response_info, forecast_mode):
         for response_table_index in range(len(response_info.response_table)):
            # Reset the current_row within the table
            self.reset_row()
            self.table[self.current_row].append(
                "DATE: "
                + str(response_info.response_table[response_table_index]["date"])
            )
            # Go to the next row
            self.next_row()
            if forecast_mode == "hourly":
                for hourly in response_info.response_table[response_table_index]["hourly"]:
                    self.table[self.current_row].append(hourly)
                    # Go to the next entry
                    self.next_row()
            else:
                entry_text = f"{response_info.response_table[response_table_index]['avg_temp']} {response_info.response_table[response_table_index]['condition']}"
                self.table[self.current_row].append(entry_text)
                # Go to the next entry
                self.next_row()


class UserInterface:
    def __init__(self) -> None:
        self.EXIT = False
        # Number of days to be convered in the forecast
        self.FORECAST_SPAN = 7
        # Which temperature unit should be displayed
        self.TEMPERATURE_UNIT = "f"
        self.NAME_OF_CITY = "Austin"
        self.FORECAST_MODE = "hourly"

    # Show the current weather

    def showCurrentWeather(self):
        # Table that holds the data to be printed
        table = []
        # Parameters for the RequestInfo constructor
        parameters = RequestParameters(number_of_days=1, city=self.NAME_OF_CITY)
        # Create an instance of RequestInfo, which will in turn
        # send a request to the online API
        info = RequestInfo(parameters=parameters)
        # Extract the response, received from the API
        try:
            res = info.getRespoonse(self.TEMPERATURE_UNIT, forecast_mode=self.FORECAST_MODE)
        except Exception as e:
            print(e)
            return

        curr_temp = str(res.response_table[0]["current_temperature"])        
        curr_date = str(res.response_table[0]["date"])
        table.append([])
        table[0] = ["CURRENT DATE: ", "CURRENT TEMPERATURE: "]
        table.append([])
        table[1] = [curr_date, curr_temp]        
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

    """Print the forecast for the current day """

    def printTodaysForecast(self):
        parameters = RequestParameters(number_of_days=1, city=self.NAME_OF_CITY)
        info = RequestInfo(parameters=parameters)
        
        try:
            res = info.getRespoonse(self.TEMPERATURE_UNIT, forecast_mode=self.FORECAST_MODE)
        except Exception as e:
            print(e)
            return        
        # For table with average temperatures use 2 rows
        if self.FORECAST_MODE == "average":
            t = TextTable(2)
            t.printForcast(response_info=res, forecast_mode=self.FORECAST_MODE)
        # For table with an hourly forecast 25 rows
        else:
            # Number of rows depends on what time it is. 25 - hour , because it includes the current hour
            rows = 25 - datetime.datetime.now().hour
            t = TextTable(rows=rows)
            t.printTodaysForecast(response_info=res, forecast_mode=self.FORECAST_MODE)

    def printForecast(self, number_of_days):
        tables = []
        table_index = 0
        parameters = RequestParameters(
            number_of_days=self.FORECAST_SPAN, city=self.NAME_OF_CITY
        )
        info = RequestInfo(parameters=parameters)

        try:
            res = info.getRespoonse(self.TEMPERATURE_UNIT, forecast_mode=self.FORECAST_MODE)
        except Exception as e:
            print(e)
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
        t.printForcast(response_info=res, forecast_mode=self.FORECAST_MODE)

    def printTable(self):
        table = TextTable(2)
        table.printTable()

    # Starting point
    def main(self):
        self.getSettings()
        # Clear the screen when starting up
        self.clearScreen()
        while self.EXIT is False:
            self.getUserInput()

    # Process user's input

    def getUserInput(self):
        self.printSwitchBoard()
        _input = input("Enter command:")
        if _input.lower() == "exit":
            self.EXIT = True
        elif _input.lower() == "today":
            self.clearScreen()
            self.printTodaysForecast()
        elif _input.lower() == "forecast":
            self.clearScreen()
            self.printForecast(self.FORECAST_SPAN)
        elif _input.lower() == "current":
            self.clearScreen()
            self.showCurrentWeather()
        elif _input.lower() == "get settings":
            self.clearScreen()
            self.getSettings()
        elif _input.lower() == "set tu":
            self.clearScreen()
            self.setTemperatureUnit()
        elif _input.lower() == "set fs":
            self.clearScreen()
            self.setForecastSpan()
        elif _input.lower() == "city":
            self.clearScreen()
            self.setNameOfCity()
        else:
            print(f"The command '{_input}' is not defined!")
    

    # Set the preferred temperature unit
    # User can choose between Fahrenheit and Celcius

    def setTemperatureUnit(self):
        unit = input("Enter temperature unit [ F / C ] :")
        if unit.lower() == "f" or unit.lower() == "c":
            self.TEMPERATURE_UNIT = unit
            if unit.lower() == "c":
                print("Temperature Unit set to Celcius!")
            else:
                print("Temperature Unit set to Fahrenheit!")
        else:
            print("You can only put F for Fahrenheit or C for Celicius!")

    def setForecastSpan(self):
        days = input("Enter number of days: ")
        setting = 0
        if days.isnumeric():
            if int(days) > 7:
                setting = 7
                print("Maximum span is 7 days, current setting is now 7 days!")
            else:
                setting = int(days)
            self.FORECAST_SPAN = setting
            self.updateSettings()
            print(f"Forecast span set to {days} days!")
        else:
            print("Number of days must be a number!")

    def setNameOfCity(self):
        city = input("Enter name of city:")
        self.NAME_OF_CITY = city.capitalize()
        self.updateSettings()
        print(f"Name of city set to {city.capitalize()}")

    def updateSettings(self):
        conf().updateSettings(
            temp_unit=self.TEMPERATURE_UNIT, forecast_span=self.FORECAST_SPAN, name_of_city=self.NAME_OF_CITY
        )
        print("Settings have been updated!")

    # Read settings from the file
    def getSettings(self):
        data = conf().getSettings()
        self.TEMPERATURE_UNIT = data["temperature_unit"]
        self.FORECAST_SPAN = data["forecast_span"]
        self.NAME_OF_CITY = data["name_of_city"]

    def printSwitchBoard(self):
        swtich_board = []
        swtich_board.append([])
        swtich_board[0] = ["DESCRIPTION", "COMMAND"]
        swtich_board.append([])
        swtich_board[1] = [
            "Show the forcast for the number of days, defined in the settings. \nDefault is 7 days, and temperature unit defaults to Fahreinheit!",
            "forecast",
        ]
        swtich_board.append([])
        swtich_board[2] = ["Show the forcast for today", "today"]
        swtich_board.append([])
        swtich_board[3] = ["Current weather", "current"]
        swtich_board.append([])
        swtich_board[4] = ["Set the temperature unit[Celcius/Fahrenheit]", "set tu"]
        swtich_board.append([])
        swtich_board[5] = [
            "Set the span of a forecast. How many days to cover? Maximum is 7!",
            "set fs",
        ]   
        swtich_board.append([])
        swtich_board[6] = ["Set name of the city for for which you want the forecast to be.\nIf not set, the setting defaults to 'Austin, TX, USA'.", "city"]     
        swtich_board.append([])
        swtich_board[7] = ["Exit", "exit"]
        print(tabulate(swtich_board, headers="firstrow", tablefmt="grid"))

    def clearScreen(self):
        os.system("cls" if os.name == "nt" else "clear")


user = UserInterface()
user.main()
