import sqlite3
from datetime import datetime, timedelta
import os
import json
import csv

def convert_date_to_str(date, format="%Y-%m-%d %H:%M"):
    return date.strftime(format)

def change_date_format(date: str, only_hour=False) -> str:
    if only_hour:
        date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        return f"{date.hour:0>2}:{date.minute:0>2}"

    date = datetime.strptime(date, "%Y-%m-%d %H:%M")
    return f"{date.day:0>2}.{date.month:0>2}.{date.year} {date.hour:0>2}:{date.minute:0>2}"

class DataBase:

    def __init__(self, open_hour, close_hour, db_path):

        self.db_path = db_path
        self._db = None
        self._cursor = None

        self.open_hour = open_hour
        self.close_hour = close_hour

    @property
    def get_current_date(self):
        return datetime.today()

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

    def has_permission_can_reservation(self, first_name, last_name):
        """
        The function check how many reservation have user.
        User cannot have more than 2 reservations in the current week.
        """
        today = self.get_current_date
        today_plus_week = today + timedelta(weeks=1)

        query = f"""
        SELECT COUNT (*) FROM reservations 
        WHERE start_date > '{convert_date_to_str(self.get_current_date)}' 
        AND start_date < '{convert_date_to_str(today_plus_week)}' 
        AND first_name = '{first_name}' AND last_name='{last_name}';
        """
        self._cursor.execute(query)

        return bool( self._cursor.fetchone()[0] < 2 )
    def has_permission_date(self, date):
        """
        The date must be at least an hour later than the current date.
        """
        return bool(
            self.get_current_date + timedelta(hours=1) < date and date < self.get_current_date + timedelta(weeks=2)
        )

    def check_availability_court(self, date):
        """
        The function check availability tennis court
        """

        query = f"""
            SELECT * FROM reservations
            WHERE start_date <= '{date.strftime("%Y-%m-%d %H:%M")}' AND end_date > '{date.strftime("%Y-%m-%d %H:%M")}';
            """
        self._cursor.execute(query)
        res = self._cursor.fetchall()

        if res:
            return
        return True

    def suggest_new_date(self, date):
        """
        The function searches for the fastest available court reservation on a given day.
        """
        open_court = datetime.strptime(self.open_hour, "%H:%M").time()
        close_court = datetime.strptime(self.close_hour, "%H:%M").time()

        new_hour_right = date + timedelta(minutes=30)
        new_hour_left = date - timedelta(minutes=30)

        query = lambda date_one: f"""
            SELECT * FROM reservations
            WHERE start_date <= '{date_one}' AND  end_date > '{date_one}';
            """


        is_close = True
        is_open = True

        while is_close or is_open:
            if is_close and close_court > new_hour_right.time():
                q = query(new_hour_right)
                self._cursor.execute(q)
                res = self._cursor.fetchall()
                if res:
                    new_hour_right += timedelta(minutes=30)
                else:
                    return new_hour_right
            else:
                is_close = False

            if is_open and new_hour_left.time() > open_court:

                q = query(new_hour_left)
                self._cursor.execute(q)
                res = self._cursor.fetchall()

                if res:
                    new_hour_left -= timedelta(minutes=30)
                else:
                    return new_hour_left
            else:
                is_open = False
        return

    def check_reservation_options(self, date):

        query = f"""
            SELECT * FROM reservations
            WHERE start_date > '{date}' AND DATE(start_date) == '{convert_date_to_str(date, "%Y-%m-%d")}'
            ORDER BY start_date;
            """
        self._cursor.execute(query)
        res = self._cursor.fetchall()
        if not res:
            # nikt nic do nie zarezerwował do końca dnia
            close_court = datetime.strptime(f'{date.year}-{date.month}-{date.day} {self.close_hour}', "%Y-%m-%d %H:%M")
            period = close_court - date
        else:
            next_reservation = res[0][3]
            period = datetime.strptime(next_reservation, "%Y-%m-%d %H:%M") - date

        if period - timedelta(minutes=90) >= timedelta(minutes=0):
            return [30, 60, 90]
        elif period - timedelta(minutes=60) >= timedelta(minutes=0):
            return [30, 60]
        elif period - timedelta(minutes=30) >= timedelta(minutes=0):
            return [30]
        else:
            return

    def take_schedule_day(self, reservation) -> str:
        """
        The function returns reservations for a specified day (reservation).
        """
        if not reservation:
            return "No Reservations\n\n"
        else:
            print_text = ''
            print_text += '\n'.join(
                f"* {i[1] + ' ' + i[2]:<30} {i[3]:<17} - {i[4]:<17}" for i in reservation
            ) + '\n\n'
        return print_text

    def save_as_json(self, name_file, from_to):

        payload = {}
        from_date = from_to[0]
        to_date = from_to[1]

        while from_date <= to_date:

            query = f"""
                    SELECT * FROM reservations
                    WHERE DATE(start_date) = '{convert_date_to_str(from_date, '%Y-%m-%d')}'
                    ORDER BY start_date;
                    """
            self._cursor.execute(query)
            res = self._cursor.fetchall()

            payload_reservation = []
            if res:
                for datum in res:
                    reservation = {
                        'name': datum[1] + ' ' + datum[2],
                        'start_time': change_date_format(datum[3], True),
                        'end_time': change_date_format(datum[4], True)
                    }
                    payload_reservation.append(reservation)
            payload[convert_date_to_str(from_date, '%d.%m')] = payload_reservation
            from_date += timedelta(days=1)
        path = os.path.join('src', 'tennis_court', 'save', name_file+'.json')
        with open(path, 'w', encoding='utf8') as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
        return True


    def save_as_csv(self, name_file, from_to):
        query = f"""
        SELECT * FROM reservations
        WHERE DATE(start_date) >= '{convert_date_to_str(from_to[0],'%Y-%m-%d')}' 
        AND DATE(end_date) <= '{convert_date_to_str(from_to[1], '%Y-%m-%d')}'
        ORDER BY start_date;
        """
        self._cursor.execute(query)
        res = self._cursor.fetchall()

        rows = [(row[1]+ ' ' + row[2], change_date_format(row[3]), change_date_format(row[4])) for row in res]
        header = ['name', 'start_date', 'end_date']

        path = os.path.join('src', 'tennis_court', 'save', name_file+'.csv')
        with open(path, 'w', encoding='utf8') as f:

            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)


    def add(self, first_name, last_name, start_date, end_date):

        start_date = convert_date_to_str(start_date)
        end_date = convert_date_to_str(end_date)
        self._cursor.execute(
            """
            INSERT INTO reservations (first_name, last_name, start_date, end_date)
            VALUES (?, ?, ?, ?)
            """,
            (first_name, last_name, start_date, end_date)
        )

        self._db.commit()
        return True

    def cancel(self, first_name, last_name, start_date):

        start_date = convert_date_to_str(start_date)
        query = f"""
        SELECT * FROM reservations
        WHERE start_date = '{start_date}' AND first_name='{first_name}' AND last_name='{last_name}';
        """

        self._cursor.execute(query)
        res = self._cursor.fetchone()

        if not res:
            return False
        else:
            query = f"""
            DELETE FROM reservations
            WHERE start_date = '{start_date}' AND first_name='{first_name}' AND last_name='{last_name}';
            """
            self._cursor.execute(query)
            self._db.commit()
            return True

    def show_schedule(self, from_date, to_date):


        while from_date <= to_date:

            from_date_str = convert_date_to_str(from_date, "%Y-%m-%d")
            query = f"""
                    SELECT * FROM reservations
                    WHERE DATE(start_date) = '{from_date_str}'
                    ORDER BY start_date;
                    """
            self._cursor.execute(query)
            res = self._cursor.fetchall()

            print_text = ""
            if from_date.date() == self.get_current_date.date():
                print_text += "Today:\n" + self.take_schedule_day(res)
            elif from_date.date() == self.get_current_date.date() + timedelta(days=1):
                print_text += 'Tomorrow:\n' + self.take_schedule_day(res)
            else:
                print_text += from_date.strftime("%A") + '\n' + self.take_schedule_day(res)

            from_date += timedelta(days=1)
            yield print_text

    def save_to_file(self, from_date, to_date, format):
        """
           The function save file as json or csv
        """
        name_file = convert_date_to_str(from_date,'%d.%m') + '-' + convert_date_to_str(to_date,'%d.%m')
        if format == '1':
            self.save_as_json(name_file, [from_date, to_date])
        elif format == '2':
            self.save_as_csv(name_file, [from_date, to_date])

    def close(self):
        self._db.close()