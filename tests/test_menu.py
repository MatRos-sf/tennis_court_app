import unittest
import threading
import queue
import os

from tennis_court.app import TennisCourtApp

DEFAULT_PATH_DB = os.path.join('test_tennis_court.db')
MENU = """
What do you want to do? Choose number: \n 
\t[1] Make a reservation
\t[2] Cancel a reservation
\t[3] Print schedule
\t[4] Save schedule to a file
\t[5] Exit\n
"""

class TestTODOAcceptance(unittest.TestCase):

    def setUp(self) -> None:
        self.inputs = queue.Queue()
        self.outputs = queue.Queue()

        self.fake_output = lambda text: self.outputs.put(text)
        self.fake_input = lambda: self.inputs.get()

        self.get_output = lambda: self.outputs.get(timeout=1)
        self.send_input = lambda response: self.inputs.put(response)

    def test_menu(self):
        app = TennisCourtApp(':memory:', io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        menu = self.get_output()
        self.assertEqual(
            menu, MENU
        )

    def test_menu_exit(self):
        app = TennisCourtApp(':memory:', io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        menu = self.get_output()
        self.assertEqual(
            menu, MENU
        )

        self.send_input('5')
        display = self.get_output()
        self.assertEqual(display, 'See you soon!\n')

    def test_menu_wrong_number(self):
        app = TennisCourtApp(':memory:', io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        menu = self.get_output()
        self.assertEqual(
            menu, MENU
        )

        self.send_input('155')
        display = self.get_output()
        self.assertEqual(display, "You should choose between 1-5.\n")
        self.send_input('aaasscasdwd')
        display = self.get_output()
        self.assertEqual(display, "You should choose between 1-5.\n")
