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

    def test_print_schedule(self):
        FakeDB().run()

        app = TennisCourtApp(
            os.path.join('src', 'tennis_court', 'db', 'temp.db'),
            io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        display = self.get_output()
        self.send_input('3')

        display = self.get_output()
        self.assertEqual(
            display,
            "Please enter the start date: "
        )

        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

    def test_print_schedule(self):
        FakeDB().run()

        app = TennisCourtApp(
            os.path.join('src', 'tennis_court', 'db', 'temp.db'),
            io=(self.fake_input, self.fake_output)
        )

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        self.get_output()
        self.send_input('3')

        self.get_output()
        day = datetime.today()
        format_date = f"{day.day:0>2}.{day.month:0>2}.{day.year}"

        self.send_input(format_date)
        new_day = datetime.today()
        format_date = f"{new_day.day:0>2}.{new_day.month:0>2}.{new_day.year}"
        self.get_output()
        self.send_input(format_date)

        display = self.get_output()
        self.assertEqual(
            display,
            'Today:\nNo Reservations\n\n'
        )
        os.remove(os.path.join('src', 'tennis_court', 'db', 'temp.db'))

