import unittest
import threading
import queue
import os
from faker import Faker
from datetime import datetime, timedelta

from tennis_court.app import TennisCourtApp
from .fake_db import FakeDB

DEFAULT_PATH_DB = os.path.join('temp.db')
MENU = """
What do you want to do? Choose number: \n 
\t[1] Make a reservation
\t[2] Cancel a reservation
\t[3] Print schedule
\t[4] Save schedule to a file
\t[5] Exit\n
"""

class TestTennisCourtApp(unittest.TestCase):

    def setUp(self) -> None:
        self.inputs = queue.Queue()
        self.outputs = queue.Queue()

        self.fake_output = lambda text: self.outputs.put(text)
        self.fake_input = lambda: self.inputs.get()

        self.get_output = lambda: self.outputs.get(timeout=1)
        self.send_input = lambda response: self.inputs.put(response)

        self.fake = Faker()

    def test_make_reservation(self):
        app = TennisCourtApp(':memory:', io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        display = self.get_output()
        self.send_input('1')

        display = self.get_output()
        self.assertEqual(
            display, "What's your Name?\n"
        )

    def test_make_reservation_correct_data(self):
        app = TennisCourtApp(':memory:', io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        display = self.get_output()
        self.send_input('1')

        display = self.get_output()
        self.assertEqual(
            display, "What's your Name?\n"
        )

        # give random name
        self.send_input(self.fake.name())

        #give date
        date = datetime.today() + timedelta(days=2)
        display = self.get_output()
        self.assertEqual(
            display, 'When would you like to book? {DD.MM.YYYY HH:MM}\n'
        )

        self.send_input(f"{date.day:0>2}.{date.month:0>2}.{date.year:0>4} 15:00")
        display = self.get_output()
        self.assertEqual(
            display, "How long would you like to book court?\n[1] 30 minutes\n[2] 60 minutes\n[3] 90 minutes\n"
        )

        # choose time
        self.send_input('2')

        display = self.get_output()
        self.assertEqual(
            display,
            "Add reservation: {}\n".format(f"{date.year:0>4}-{date.month:0>2}-{date.day:0>2} 15:00:00")
        )

    def test_make_reservation_incorrect_name(self):
        app = TennisCourtApp(':memory:', io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        display = self.get_output()
        self.send_input('1')

        display = self.get_output()
        self.assertEqual(
            display, "What's your Name?\n"
        )

        # incorrect name -- no space
        self.send_input('JanKowalski')
        display = self.get_output()
        self.assertEqual(
            display,
            ("\nThe name should consist of a first name and last name separate space e.g Jan Kowalski.\n"
            "and\n"
            "The name should consist only of letters.\n\n")
        )

        # incorrect name -- include number
        display = self.get_output()
        self.send_input('Jan k0walski')
        display = self.get_output()
        self.assertEqual(
            display,
            ("\nThe name should consist of a first name and last name separate space e.g Jan Kowalski.\n"
            "and\n"
            "The name should consist only of letters.\n\n")
        )

        # quit
        display = self.get_output()
        self.send_input('QUIT')
        display = self.get_output()

        self.assertEqual(
            display,
            "Press enter to continue.\n"
        )

    def test_make_reservation_incorrect_date(self):
        app = TennisCourtApp(':memory:', io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        display = self.get_output()
        self.send_input('1')

        display = self.get_output()
        self.assertEqual(
            display, "What's your Name?\n"
        )


        self.send_input(self.fake.name())
        display = self.get_output()
        self.assertEqual(
            display,
            'When would you like to book? {DD.MM.YYYY HH:MM}\n')

        # incorrect date
        date = f"12332213213"
        self.send_input(date)
        display = self.get_output()
        self.assertEqual(
            display,
            (
                "Format date should be {DD.MM.YYYY HH:MM} e.g. 26.03.2023 15:30.\n"
                "And\n"
                "Reservations can only be made on the hour or half-hour. Please choose a valid reservation time.\n"
            )
        )

        # incorrect date -- minutes
        display = self.get_output()
        date = datetime.today() + timedelta(days=2)
        self.send_input(f"{date.day:0>2}.{date.month:0>2}.{date.year:0>4} 11:36")
        display = self.get_output()
        self.assertEqual(
            display,
            (
                "Format date should be {DD.MM.YYYY HH:MM} e.g. 26.03.2023 15:30.\n"
                "And\n"
                "Reservations can only be made on the hour or half-hour. Please choose a valid reservation time.\n"
            )
        )

        # incorrect date -- quit
        display = self.get_output()
        self.send_input('quit')
        display = self.get_output()
        self.assertEqual(
            display,
            "What's your Name?\n"
        )


class TestTennisCourtAppWithDB(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = queue.Queue()
        self.outputs = queue.Queue()

        self.fake_output = lambda text: self.outputs.put(text)
        self.fake_input = lambda: self.inputs.get()

        self.get_output = lambda: self.outputs.get(timeout=1)
        self.send_input = lambda response: self.inputs.put(response)

        self.fake = Faker()

    def test_make_reservation_has_not_permission_can_reservation(self):
        FakeDB().run()

        app = TennisCourtApp(
                    os.path.join('src', 'tennis_court', 'db', 'temp.db'), io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()


        self.get_output(), self.send_input('1')
        self.get_output(), self.send_input("Jan Kowalski")

        date = datetime.today() + timedelta(days=5)
        display = self.get_output()
        self.assertEqual(
            display, 'When would you like to book? {DD.MM.YYYY HH:MM}\n'
        )
        self.send_input(f"{date.day:0>2}.{date.month:0>2}.{date.year:0>4} 11:00")
        display = self.get_output()
        self.assertEqual(
            display, "User cannot have more than 2 reservations in the current week.\n"
        )

        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

    def test_make_reservation_has_not_permission_date(self):
        FakeDB().run()

        app = TennisCourtApp(
                    os.path.join('src', 'tennis_court', 'db', 'temp.db'), io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()


        self.get_output(), self.send_input('1')
        self.get_output(), self.send_input("Test test")

        date = datetime.today()
        display = self.get_output()
        self.assertEqual(
            display, 'When would you like to book? {DD.MM.YYYY HH:MM}\n'
        )
        self.send_input(f"{date.day:0>2}.{date.month:0>2}.{date.year:0>4} {date.hour:0>2}:30")
        display = self.get_output()
        self.assertEqual(
            display, "The date must be at least an hour later than the current date.\n"
        )

        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

    def test_make_reservation_no_place(self):
        FakeDB().run()

        app = TennisCourtApp(
                    os.path.join('src', 'tennis_court', 'db', 'temp.db'), io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()


        self.get_output(), self.send_input('1')
        self.get_output(), self.send_input('Jan test')

        date = datetime.today() + timedelta(days=1)
        display = self.get_output()
        self.assertEqual(
            display, 'When would you like to book? {DD.MM.YYYY HH:MM}\n'
        )
        self.send_input(f"{date.day:0>2}.{date.month:0>2}.{date.year:0>4} 12:30")
        display = self.get_output()
        self.assertEqual(
            display, "All hours are occupied on this day. Choose different date.\n"
        )

        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

    def test_make_reservation_unavailable_date(self):
        FakeDB().run()

        app = TennisCourtApp(
                    os.path.join('src', 'tennis_court', 'db', 'temp.db'), io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()


        self.get_output(), self.send_input('1')
        self.get_output(), self.send_input('Jan test')

        date = datetime.today() + timedelta(days=3)
        display = self.get_output()
        self.assertEqual(
            display, 'When would you like to book? {DD.MM.YYYY HH:MM}\n'
        )
        self.send_input(f"{date.day:0>2}.{date.month:0>2}.{date.year:0>4} 09:30")
        display = self.get_output()
        self.assertEqual(
            display,
            ("The time you chose is unavailable, "
            f"would you like to make a reservation for 10:00:00 instead? (yes/no)\n")
        )
        self.send_input('y')
        display = self.get_output()
        self.assertEqual(
            display,
            "How long would you like to book court?\n" + "[1] 30 minutes\n"
        )

        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

    def test_make_reservation_unavailable_date_options(self):
        FakeDB().run()

        app = TennisCourtApp(
                    os.path.join('src', 'tennis_court', 'db', 'temp.db'), io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()


        self.get_output(), self.send_input('1')
        self.get_output(), self.send_input('Jan test')

        date = datetime.today() + timedelta(days=3)
        display = self.get_output()
        self.assertEqual(
            display, 'When would you like to book? {DD.MM.YYYY HH:MM}\n'
        )
        self.send_input(f"{date.day:0>2}.{date.month:0>2}.{date.year:0>4} 10:00")
        display = self.get_output()
        self.assertEqual(
            display,
            "How long would you like to book court?\n[1] 30 minutes\n"
        )

        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))