# Introduction
The script provides means to get a weather forecast or current temperature and weather conditions in any city on the planet,
as long as the API that I am using to get the data from, covers that city in their database. The script is intended to run in a terminal of a machine with a pre-installed Python Interpreter.
# Preparation
## Finding an API
I had to find an online API that meets the following requirements:
1. It is a free online API
2. It allows to choose the name of a city, instead of longitute and latitude coordinates
I read some reviews and narrowed it down to [Weather-API](https://www.weatherapi.com/)
I registered myself with the provider of the API and received an API-key.
# ISSUES
## Migration to a different repository
I started working on the Project as sson as I learned the most basic things about Python. So I manually created a repository on GitHub
and started working locally on VS Code.
Later on, during my second session with my mentor he said that we were supposed to use a template, provided by code institute
and deploy the project on Heroku.
To cut the long story short, I exported the Project to a different repository, that was created using the template. Therefore, the first
batch of commits is missing in the currently used repository.
There were only four commits in total and the intial source code. Here is the link to the first repository if you find it relevant 
[First repo](https://github.com/dimitri-edel/pp3.git)
## Size of the terminal
At first I adjusted the size of the terminal in the index.html that came with the template. It allowed me to have more space and create
larger tables, which could accomodate forecasts for up to seven days, without making it look messy. Neither me, nor my mentor were sure 
about how the assemsment team would feel about me changing the files, which Code Institute warned us agains changing. So, toward the end
I changed it back to the intial width of 80 columns. It's like they say: 'Customer is King!'
## API trial ended
That resolves the question about the size of the terminal. Because, today on 21st of April 2023, I received an email informing me that the trial period had ended. As a consequence, my account had been added to the free plan, which only provides three days of forecast.
## Single User (Heroku)
The Project has been deployed on Heroku, which is a public website and can be used by many people at the same time. In the course that I am currently enrolled in, we have not yet gotten around to session management with Python.
The project does not use a session or a database to store user data. If several users try to change the generated settings file at the same time, it will result in data inconsistency. The script is not intended for this purpose. It is intended to be copied to a particular machine and run locally.
Heroku merely serves as a platform for presentation purposes. However, I will implement session management in the project later on and store the settings in the session instead of storing them in a file.
# User stories
## Information on the current weather at a certain location
## Getting the current day's weather forecast for a certain locatioon
## Getting several days of the weather forecast for a certain locatioon
## Switching between temperature units
## Switching between names of location
## Swtiching between forecast modes
## Entering invalid data

# Code
## OOD
### Class diagram
### Flow chart
## BUGS
### API sometimes delivers more datasets than expected
A nasty bug found its way into my work today. The API started to deliver more hourly reports per day than the usual 24 hours.
This resulted in an index error in TextTable.addForecastColumns()-method, within the loop. The enty_index was getting out
of range. Took me over an hour of debugging and wrecking my mind to finally pin down the problem. I have no idea as to 
why the API started appending more hours, which technically belong in the dataset of the next day. However, I simply added
two lines of code in the loop, which check if the number of datasets exceed 24 (as in 24 hours), then these datasets will be
skipped.

### Can not get textwrapper.dedent() method to do what it is supposed to do
The textwraper.dedent() method is not doing what it's supposed to. After applying it the text still appears indented in the
TextTable. Found this on stackoverflow.com <code> print('\n'.join([m.lstrip() for m in message.split('\n')]))</code>.
I adjusted that to my code and it worked, the multi-line text appears without indentions.

### An empty dataset appears in the forecast table 
The issue stemmed from a loop inside RequestInfo.__extract_forecast(). 
# Technologies
- GitHub
- VS Code
- Heroku
- Python
# Deployment
## Local machine
If someone wants to use it on their local machine, they would have to copy the folders **conf** and **src** and the file **run.py** to a folder of their choice and then execute **run.py** on their machine. 
### Special request
If you intend to use it on your computer, then **PLEASE**  get an **API KEY** for yourself! It is **easy** to do. You only need to sign up at [Weather-API website](https://www.weatherapi.com/). All you need to provide is a valid **email-address** and **it does not cost a thing**. Then just copy the **API-key** into to the constructor of the class named RequestInfo in api.py. The name of the property in the constructor is **API_KEY**.
## Heroku

# Credits
## Code Institute
Code Instititute provideed the tutorials on essential knowledge of Python.
The template for the Heroku website and a step by step tutorial on how to deploy a project on Heroku was provided by the friendly team of Code Institute.
## stackoverflow.com
Provided solutions for a few problems, which I would not have been able to come up with on my own.
## w3schools.com
I oftentimes used this website, when I needed to quickly look up how to use certain classes and functions in Python. It posed a great helper in additon to the tutorials by Code Institute.
## My mentor Adegbenga Adeye
Special thanks to my mentor for the help and support throughout the project!

