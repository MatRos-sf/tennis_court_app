import os
import sqlite3
from datetime import datetime, timedelta

class FakeDB:
    def __init__(self, db_path=os.path.join('src', 'tennis_court', 'db', 'temp.db')):
        self.db_path = db_path
        self._db = None
        self._cursor = None
    def set_db(self):
        """
        The function connects to the database or create the one and sets up the cursor.
        """
        self._db = sqlite3.connect(self.db_path)
        self._cursor = self._db.cursor()

        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            start_date DATETIME NOT NULL,
            end_date NOT NULL
            )
            """
        )

    def run(self):

        self.set_db()
        day = datetime.today() + timedelta(days=1)
        format_date = lambda x:f"{x.year}-{x.month:0>2}-{x.day:0>2}"

        # 1 options
        self._cursor.execute(
            """
            INSERT INTO reservations (first_name, last_name, start_date, end_date)
            VALUES (?, ?, ?, ?)
            """,
            ("Jan", "Kowalski", format_date(day)+ ' 09:00', format_date(day) + ' 21:00')
        )
        self._db.commit()
        # 2 option
        day += timedelta(days=1)
        self._cursor.executemany(
            """
            INSERT INTO reservations (first_name, last_name, start_date, end_date)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("Weronika", "Jaks", format_date(day)+ ' 10:00', format_date(day) + ' 20:00')
            ]
        )
        self._db.commit()
        # 3 options
        day += timedelta(days=1)
        self._cursor.executemany(
            """
            INSERT INTO reservations (first_name, last_name, start_date, end_date)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("Adam", "Lewanowski", format_date(day)+ ' 09:00', format_date(day) + ' 10:00'),
                ("Iwona", "Zamkowska", format_date(day) + ' 10:30', format_date(day) + ' 11:30'),
                ("Marcin", "Mallek", format_date(day) + ' 12:30', format_date(day) + ' 13:00'),
                ("Jan", "Kowalski", format_date(day) + ' 14:30', format_date(day) + ' 15:00'),
            ]
        )
        self._db.commit()
        self._db.close()