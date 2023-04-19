import os  # import operating system routines


class Configuration:
    def update_settings(self, temp_unit, forecast_span, name_of_city):
        file_content = "tu=" + temp_unit + \
            " " + "days=" + str(forecast_span) + \
                " " + "city=" + name_of_city
        path = os.path.normcase("./conf/settings.sf")
        f = open(path, "w")
        f.write(file_content)
        f.close()
        data = {'temperature_unit': temp_unit, 'forecast_span': forecast_span}
        return data

    # Read settings from the file
    def get_settings(self):
        data = {'temperature_unit': "", 'forecast_span': 0, "name_of_city": ""}
        try:
            path = os.path.normcase("./conf/settings.sf")
            f = open(path, "r")
            file_content = f.read()
            split_content = file_content.split(" ")
            tu = split_content[0].split("=")
            days = split_content[1].split("=")
            city = split_content[2].split("=")
            data["temperature_unit"] = tu[1]
            data["forecast_span"] = int(days[1])
            data["name_of_city"] = city[1]
            return data
        except FileNotFoundError:
            # Create settings-file using default values
            return self.update_settings(temp_unit='f', forecast_span=7, name_of_city="London")
