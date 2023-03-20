from flask import Flask, request, render_template
from datetime import datetime, timedelta
from icalendar import Calendar
import requests
import os

app = Flask(__name__)

BOOKIPY_URL = 'https://api.bookiply.com/pmc/rest/apartments/43146778/ical.ics?key=' + os.environ.get('BOOKIPLY_API_Key')


def get_month_data(year, month):
    # Get iCal File
    response = requests.get(BOOKIPY_URL)
    content = response.text

    # Verarbeiten Sie den Inhalt der iCal-Datei
    cal = Calendar.from_ical(content)
    booked_dates = []

    # Iterieren Sie durch alle Ereignisse im Kalender
    for event in cal.walk('VEVENT'):
        start = event.get('DTSTART').dt
        end = event.get('DTEND').dt

        # Fügen Sie alle Daten zwischen Start- und Enddatum hinzu
        current_date = start
        while current_date <= end:
            booked_dates.append(current_date)
            current_date += timedelta(days=1)

    # Erstellen Sie eine Liste mit Daten für den angegebenen Monat und Jahr
    month_data = []
    today = datetime.today()
    # Berechnen Sie das letzte Datum des Monats
    last_day_of_month = datetime(year, month, 1) + timedelta(days=32)
    last_day_of_month = last_day_of_month.replace(day=1) - timedelta(days=1)
    for day in range(1, last_day_of_month.day + 1):
        date = datetime(year, month, day)
        status = "free"
        # flat is free at last and first day of booking:
        # could cause problems, if flat is booked just one day!
        if (date.date() in booked_dates) and (date.date() - timedelta(1) in booked_dates) and (date.date() + timedelta(1) in booked_dates):
            status = "booked"
        if date < today.replace(hour=0, minute=0, second=0, microsecond=0):
            status = "past"
        day_data = {
            "date": date,
            "status": status
        }
        month_data.append(day_data)
    return month_data


def calculate_monthStartDays(dates):
    month_start = dates[0].get('date')
    first_weekday = month_start.weekday()
    for i in range(1, first_weekday + 1):
        temp_date = day_data = {
            "date": month_start - timedelta(i),
            "status": 'start'
        }
        dates.insert(0, temp_date)
    return dates


def calculate_weeks(dates):
    weeks = []
    current_week = [None] * 7
    current_weekday = 0
    for day in dates:
        current_week[current_weekday] = day
        current_weekday = (current_weekday + 1) % 7
        if current_weekday == 0 or day == dates[len(dates) - 1]:
            weeks.append(current_week)
            current_week = [None] * 7
    # remove all None values from last week
    weeks[len(weeks) - 1] = [i for i in weeks[len(weeks) - 1] if i is not None]
    return weeks


def get_Infos(month, year):
    prev_date = datetime(year, month, 1) - timedelta(days=1)
    next_date = datetime(year, month, 1) + timedelta(days=32)
    months = {
        1: "Januar",
        2: "Februar",
        3: "März",
        4: "April",
        5: "Mai",
        6: "Juni",
        7: "Juli",
        8: "August",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Dezember"
    }
    infos = {
        'month_text': months.get(month),
        'year': year,
        'prev_year':    prev_date.strftime("%Y"),
        'prev_month':   prev_date.strftime("%m"),
        'next_year':    next_date.strftime("%Y"),
        'next_month':   next_date.strftime("%m")
    }
    return infos


@app.route('/availability')
def get_availability():
    today = datetime.today()
    year = request.args.get('year', default=today.year, type=int)
    month = request.args.get('month', default=today.month, type=int)
    if month not in range(1, 13):
        return render_template('error.html', message='ValueError: month must be in 1..12 or empty')
    dates = get_month_data(year, month)
    dates = calculate_monthStartDays(dates)
    weeks = calculate_weeks(dates)
    infos = get_Infos(month, year)
    fa_key = os.environ.get('fa_API_KEY')
    return render_template('calendar.html', weeks=weeks,  infos=infos, fa_key=fa_key)


@app.route('/test')
def test():
    return 'test'


@app.route('/')
def index():
    return 'Welcome to Availability checker for holiday apartment Haidle.' \
           'Please visit us on ferienwohnung-haidle.de'


if __name__ == '__main__':
    app.run()
