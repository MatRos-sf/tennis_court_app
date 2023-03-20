import os
import sys
import functools
from datetime import datetime, timedelta

from .control_db import DataBase
from dotenv.main import load_dotenv

load_dotenv()

try:
    OPEN = os.environ['OPEN']
    CLOSE = os.environ['CLOSE']

except Exception:
    sys.exit()

DEFAULT_PATH_DB = os.path.join('src', 'tennis_court', 'db', 'tennis_court.db')

MENU = """
What do you want to do? Choose number: \n 
\t[1] Make a reservation
\t[2] Cancel a reservation
\t[3] Print schedule
\t[4] Save schedule to a file
\t[5] Exit\n
"""

class TennisCourtApp:

    def __init__(self, path_db=DEFAULT_PATH_DB, io=(input, functools.partial(print, end=""))):
        self._in, self._out = io
        self.path_db = path_db
        self._db = None
        self._quit = False

    def _check_response(self, response, possibility):

        if response.lower().strip() == 'quit':  return 'quit'
        if response.lower().strip() not in possibility:
            return
        return response

    def _check_fullname_response(self, response):

        if response.lower() == 'quit':
            return 'quit', 'quit'
        # name consist: first name and last name
        if len(response.split()) == 2:
            first_name, last_name = response.title().split()
        else:
            return None, None

        #
        if first_name.isalpha() and last_name.isalpha():
            return first_name, last_name
        else:
            return None, None

    def _check_date_response(self, response, only_date=False):
        """
        The function return correctly reservation date (datetime) or None
        """
        if response.lower() == 'quit':
            return 'quit'

        # check good form date
        try:
            if only_date:
                correct_date = datetime.strptime(response, "%d.%m.%Y")
            else:
                correct_date = datetime.strptime(response, "%d.%m.%Y %H:%M")
        except ValueError:
            return

        # check property hour or minute
        if not only_date and correct_date.minute not in [0, 30]:
            return

        # change format date
        if only_date:
            response = f"{correct_date.year}-{correct_date.month:0>2}-{correct_date.day:0>2} " \
                       f"{OPEN}"
        else:
            response = f"{correct_date.year}-{correct_date.month:0>2}-{correct_date.day:0>2} " \
                   f"{correct_date.hour:0>2}:{correct_date.minute:0>2}"

        return datetime.strptime(response, "%Y-%m-%d %H:%M")

    def exit(self):
        self._quit = True

    def run(self):

        # open database
        self._db = DataBase(OPEN, CLOSE, self.path_db)
        self._db.set_db()

        self._out(MENU)

        # main loop
        while not self._quit:

            response = self._in()
            match self._check_response(response, list('12345')):
                case '1':
                    self.make_reservation()
                case '2':
                    self.cancel_reservation()
                case '3':
                    self.print_schedule()
                case '4':
                    self.save_schedule()
                case '5':
                    self.exit()
                    continue
                case _:
                    self._out("You should choose between 1-5.\n")
                    continue
            self._out("Press enter to continue.\n")
            self._in()
            self._out(MENU)

        self._out('See you soon!\n')
        self._db.close()

    def make_reservation(self):

        first_name, last_name = None, None
        reservation_date = None

        while not all([ first_name, last_name, reservation_date ]):
            # take full name
            if not all([first_name, last_name]):
                self._out("What's your Name?\n")
                # take correct full name
                response = self._in()
                first_name, last_name = self._check_fullname_response(response)
                # Conditions
                if first_name == 'quit':
                    break
                elif not all([first_name, last_name]):
                    self._out(
                        "\nThe name should consist of a first name and last name separate space e.g Jan Kowalski.\n"
                        "and\n"
                        "The name should consist only of letters.\n\n",
                    )
                    continue

            # take date
            if not reservation_date:
                self._out('When would you like to book? {DD.MM.YYYY HH:MM}\n')
                response = self._in()
                reservation_date = self._check_date_response(response)
                # Conditions
                if reservation_date == 'quit':
                    # take back to the previous step
                    first_name, last_name, reservation_date = None, None, None
                    continue
                if not reservation_date:
                    self._out(
                        "Format date should be {DD.MM.YYYY HH:MM} e.g. 26.03.2023 15:30.\n"
                        "And\n"
                        "Reservations can only be made on the hour or half-hour. Please choose a valid reservation time.\n"
                    )
                    continue

            # check conditionals
            if not self._db.has_permission_can_reservation(first_name, last_name):
                self._out("User cannot have more than 2 reservations in the current week.\n")
                break
            elif not self._db.has_permission_date(reservation_date):
                self._out("The date must be at least an hour later than the current date.\n")
                break

            # check availability
            if not self._db.check_availability_court(reservation_date):
                reservation_date = self._db.suggest_new_date(reservation_date)
                if not reservation_date:
                    self._out("All hours are occupied on this day. Choose different date.\n")
                    reservation_date = None
                    continue
                else:
                    self._out("The time you chose is unavailable, "
                              f"would you like to make a reservation for {reservation_date.time()} instead? (yes/no)\n")
                    response = self._in()
                    if self._check_response(response, ['yes', 'y', 'no', 'n']) and response.lower() in ['no', 'n']:
                        reservation_date = None
                        continue

            reservation_options = self._db.check_reservation_options(reservation_date)
            if not reservation_options:
                self._out(f"You chose probably invalid date. Make sure that your hour is between: {OPEN} - {CLOSE}\n")
                reservation_date = None
                continue

            out = ""
            for index, t in enumerate(reservation_options):
                out += f"[{index + 1}] {t} minutes\n"
            self._out("How long would you like to book court?\n" + out)
            response = self._in()
            chosen_option = self._check_response(response, [str(i) for i in range(1,len(reservation_options)+1)])
            if chosen_option == 'quit':
                reservation_date = None
            elif not chosen_option:
                continue
            end_date = reservation_date + timedelta(minutes=[30,60,90][int(response)-1])
        else:
            self._db.add(first_name, last_name, reservation_date, end_date)
            self._out(f"Add reservation: {reservation_date}\n")

    def cancel_reservation(self):

        first_name, last_name = None, None
        start_date = None

        while not all([first_name, last_name, start_date]):

            # take name
            if not first_name:
                self._out("Please enter the full name of the person whose reservation you want to cancel.\n")
                response = self._in()
                first_name, last_name = self._check_fullname_response(response)
                if first_name == 'quit':
                    # go back to menu
                    break
                elif not all([first_name, last_name]):
                    self._out(
                        "\nThe name should consist of a first name and last name separate space e.g Jan Kowalski.\n"
                        "and\n"
                        "The name should consist only of letters.\n\n",
                    )
                    continue

            # take date
            if not start_date:
                self._out("Please enter the reservation date. {DD.MM.YYYY HH:MM}\n")
                response = self._in()
                start_date = self._check_date_response(response)
                if start_date == 'quit':
                    first_name, last_name = None, None
                    continue
                if not start_date:
                    self._out(
                        "Format date should be {DD.MM.YYYY HH:MM} e.g. 26.03.2023 15:30.\n"
                        "And\n"
                        "Reservations can only be made on the hour or half-hour. Please choose a valid reservation time.\n"
                    )
                    continue

            # Conditional
            if not self._db.has_permission_date(start_date):
                self._out("The date must be at least an hour later than the current date.\n")
        else:
            is_cancel = self._db.cancel(first_name, last_name, start_date)
            if not is_cancel:
                self._out("You have provided incorrect data.\n")
            else:
                self._out(f"The reservation ({start_date}) has been cancelled.\n")

    def print_schedule(self):
        from_date, to_date = None, None

        while not all([from_date, to_date]):

            if not from_date:
                self._out("Please enter the start date: ")
                response = self._in()
                from_date = self._check_date_response(response, True)
                if from_date == 'quit':
                    # back to the menu
                    break
                if not from_date:
                    self._out(
                        "Format date should be {DD.MM.YYYY} e.g. 26.03.2023.\n"
                    )
                    continue
            if not to_date:
                self._out("Please enter the end date: ")
                response = self._in()
                to_date = self._check_date_response(response, True)
                if to_date == 'quit':
                    # take back to the previous step
                    from_date = None
                    continue
                if not to_date:
                    self._out(
                        "Format date should be {DD.MM.YYYY} e.g. 26.03.2023.\n"
                    )
                    continue

            now = datetime.today().date()
            if from_date and to_date:
                # from_date must be less than to_date
                if from_date.date() > to_date.date():
                    from_date, to_date = to_date, from_date


        else:
            for single_day in self._db.show_schedule(from_date, to_date):
                self._out(single_day)

    def save_schedule(self):
        from_date, to_date = None, None

        while not all([from_date, to_date]):

            if not from_date:
                self._out("Please enter the start date: ")
                response = self._in()
                from_date = self._check_date_response(response, True)
                if from_date == 'quit':
                    # back to the menu
                    break
                if not from_date:
                    self._out(
                        "Format date should be {DD.MM.YYYY HH:MM} e.g. 26.03.2023.\n"
                    )
                    continue

            if not to_date:
                self._out("Please enter the end date: ")
                response = self._in()
                to_date = self._check_date_response(response, True)
                if to_date == 'quit':
                    # take back to the previous step
                    from_date = None
                    continue
                if not to_date:
                    self._out(
                        "Format date should be {DD.MM.YYYY} e.g. 26.03.2023.\n"
                    )
                    continue

            now = datetime.today().date()
            if from_date and to_date:
                # from_date must be less than to_date
                if from_date.date() > to_date.date():
                    from_date, to_date = to_date, from_date


            self._out(
                "What format do you want to save the data in?\n[1] json\n[2] csv\n"
            )
            response_format = self._in()
            if self._check_response(response_format, ['1', '2']) == 'quit':
                to_date = None
        else:
            self._db.save_to_file(from_date, to_date, response_format)
            self._out("The file has been saved.\n")
