import unittest
import threading
import queue
import os
from faker import Faker
from datetime import datetime, timedelta

from tennis_court.app import TennisCourtApp
from .fake_db import FakeDB

class TestTennisCourtApp(unittest.TestCase):

    def setUp(self) -> None:
        self.inputs = queue.Queue()
        self.outputs = queue.Queue()

        self.fake_output = lambda text: self.outputs.put(text)
        self.fake_input = lambda: self.inputs.get()

        self.get_output = lambda: self.outputs.get(timeout=1)
        self.send_input = lambda response: self.inputs.put(response)

        self.fake = Faker()

    def test_cancel_reservation(self):
        FakeDB().run()

        app = TennisCourtApp(
            os.path.join('src', 'tennis_court', 'db', 'temp.db'),
            io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        display = self.get_output()
        self.send_input('2')

        display = self.get_output()
        self.assertEqual(
            display,
            "Please enter the full name of the person whose reservation you want to cancel.\n"
        )

        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

    def test_cancel_reservation_successful(self):
        FakeDB().run()

        app = TennisCourtApp(
            os.path.join('src', 'tennis_court', 'db', 'temp.db'),
            io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        self.get_output()
        self.send_input('2')

        self.get_output()
        self.send_input('Weronika Jaks')

        day = datetime.today() + timedelta(days=2)
        format_date = f"{day.day:0>2}.{day.month:0>2}.{day.year} 10:00"

        self.get_output()
        self.send_input(format_date)

        display = self.get_output()
        self.assertEqual(
            display,
            f"The reservation ({day.year}-{day.month:0>2}-{day.day:0>2} 10:00:00)"
            f" has been cancelled.\n"
        )
        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

    def test_cancel_reservation_unsuccessful(self):
        FakeDB().run()

        app = TennisCourtApp(
            os.path.join('src', 'tennis_court', 'db', 'temp.db'),
            io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        self.get_output()
        self.send_input('2')

        self.get_output()
        self.send_input(self.fake.name())

        day = datetime.today() + timedelta(days=2)
        format_date = f"{day.day:0>2}.{day.month:0>2}.{day.year} 10:00"

        self.get_output()
        self.send_input(format_date)

        display = self.get_output()
        self.assertEqual(
            display,
            "You have provided incorrect data.\n"
        )
        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

