# Tennis court app

Author: Mateusz Rosenkranz, mateuszrosenkranz@gmail.com
Tennis court app is a simple application created as a recruitment task. 

The project is divided into two main folders: `src` and `tests`. 
The `tests` folder contains tests for the application, while the `src` folder contains the project itself. 
The database will appear in `src/tennis_court/db` when the project is launched, and 
the application will save created .json and .csv files in `src/tennis_court/save`.

## Installation

To install the necessary libraries, first clone the project.
```shell
git clone git@github.com:MatRos-sf/tennis_court_app.git
```
Then, create a Python virtual environment using:
```shell
python -m venv venv
```
activate it:
* Windows: `venv\Scripts\activate`
* Unix/Linux: `source venv/bin/activate`

and install the libraries using 
```shell
pip install -r requirements.txt
```
Finally, run the development mode using:
```shell
pip install -e src/
```
### Usage

To run the application, use the command
```shell
python -m tennis_court
```

To run tests, use the command:
```shell
python -m unittest discover -v
```

The application uses an SQLite3 database and requires Python 3.10 or higher. 
It allows users to add/cancel/display reservations and save them in .json or .csv format. 

Before running the application, you must create a `.env` file in `src/tennis court/` 
with the opening and closing times of the court in the following format:
```text
OPEN=9:00
CLOSE=21:00
```

### Additional information 

A `fake_db.py` file was created in the `tests` folder to create a temporary database for testing purposes. 
It is automatically deleted after the tests are run.

The main `TennisCourtApp` class responsible for the program's operation can be found in `src/tennis_court/app.py`.

The `DataBase` class responsible for database queries is located in `src/tennis_court/control_db.py`.