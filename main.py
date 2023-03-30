from flask import Flask, request, render_template, url_for, flash, redirect
from datetime import datetime, timedelta
from icalendar import Calendar
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('Flask_Secret_Key_FEWO')

BOOKIPY_URL = 'https://api.bookiply.com/pmc/rest/apartments/43146778/ical.ics?key=' + os.environ.get('BOOKIPLY_API_Key')
# booked_dates may could occur errors, if two requests at same time?!
# used in get_month_data (read and write) and calculate_monthStartDays (write)
booked_dates = []


def get_month_data(year, month):
    # Get iCal File
    response = requests.get(BOOKIPY_URL)
    content = response.text

    # Verarbeiten Sie den Inhalt der iCal-Datei
    cal = Calendar.from_ical(content)
    global booked_dates
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
        day_data = {
            "date": date,
            "status": calculateStatusofDate(date)
        }
        month_data.append(day_data)
    return month_data


def calculateStatusofDate(date):
    status = "free"
    # flat is free at last and first day of booking:
    # could cause problems, if flat is booked just one day!
    if (date.date() in booked_dates) and (date.date() - timedelta(1) in booked_dates) and (
            date.date() + timedelta(1) in booked_dates):
        status = "booked"
    # set start/ end of a booking
    if date.date() in booked_dates and status == "free":
        if date.date() - timedelta(1) not in booked_dates:
            status = "begin"
        else:
            status = "end"
    today = datetime.today()
    if date < today.replace(hour=0, minute=0, second=0, microsecond=0):
        status = "past"
    return status


# add days (Monday to weekday of day 1 of month) to dates
def calculate_monthStartDays(dates):
    month_start = dates[0].get('date')
    first_weekday = month_start.weekday()
    for i in range(1, first_weekday + 1):
        temp_date = {
            "date": month_start - timedelta(i),
            "status": calculateStatusofDate(month_start - timedelta(i))
        }
        dates.insert(0, temp_date)
    return dates


# split dates in list of weeks for correct output of calendar
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
    # set days at end of month belong to next month
    i = 1
    tempLastWeek = []
    for day in weeks[len(weeks) - 1]:
        if day is None:
            temp_date = {
                "date": dates[len(dates) - 1].get('date') + timedelta(i),
                "status": calculateStatusofDate(dates[len(dates) - 1].get('date') + timedelta(i))
            }
            tempLastWeek.append(temp_date)
            i += 1
        else:
            tempLastWeek.append(day)
    weeks[len(weeks) - 1] = tempLastWeek
    return weeks


def get_Infos(month, year):
    today = datetime.today()
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
        'thisYear': today.strftime("%Y"),
        'prev_year': prev_date.strftime("%Y"),
        'prev_month': prev_date.strftime("%m"),
        'next_year': next_date.strftime("%Y"),
        'next_month': next_date.strftime("%m")
    }
    return infos


@app.route('/requestbooking', methods=['GET', 'POST'])
def requestBooking():
    if request.method == 'POST':
        postValid = True
        mail = request.form['email']
        firstName = request.form['first-name']
        lastName = request.form['last-name']
        startDate = request.form['start-date']
        endDate = request.form['end-date']
        adults = int(request.form['adults'])
        children = int(request.form['children'])
        sendConfirmation = "confirmation-mail" in request.form

        if not mail:
            flash('Mail is required!', 'error')
            postValid = False
        if not firstName:
            flash('First-Name is required!', 'error')
            postValid = False
        if not lastName:
            flash('Last-Name is required!', 'error')
            postValid = False
        if not startDate:
            flash('Start-Date is required!', 'error')
            postValid = False
        if not endDate:
            flash('End-Date is required!', 'error')
            postValid = False
        if adults + children == 0:
            flash('At least one person is required!', 'error')
            postValid = False
        if adults + children > 4:
            flash('Maximum 4 persons are allowed!', 'error')
            postValid = False
        if postValid:
            print("Handle request now")
            # Handle request
            # send submit mail
            # msg = Message('Anfrage für Ferienwohnung',)
            # msg.add_recipient(mail)
            # msg.body = "Hallo " + firstName + " " + lastName + ",\n\n" + "vielen Dank für Ihre Anfrage für die Ferienwohnung. Wir werden uns schnellstmöglich bei Ihnen melden.\n\n" + "Mit freundlichen Grüßen\n\n" + "Familie Schröder"
            # mail.send(msg)
            # # send admin mail
            # msg = Message('Anfrage für Ferienwohnung',)
            # msg.add_recipient(os.environ.get('ADMIN_MAIL'))
            # msg.body = "Hallo Admin,\n\n" + "es gibt eine neue Anfrage für die Ferienwohnung. Bitte prüfen Sie die Anfrage und melden Sie sich bei dem Gast.\n\n" + "Mit freundlichen Grüßen\n\n" + "Familie Schröder"
            # mail.send(msg)
            flash('Vielen Dank für deine Buchungsanfrage! '
                  'Wir haben diese erhalten und melden uns schnellstmöglich bei dir.', 'success')
            if sendConfirmation:
                # send submit mail
                # msg = Message('Anfrage für Ferienwohnung',)
                # msg.add_recipient(mail)
                # msg.body = "Hallo " + firstName + " " + lastName + ",\n\n" + "vielen Dank für Ihre Anfrage für die Ferienwohnung. Wir werden uns schnellstmöglich bei Ihnen melden.\n\n" + "Mit freundlichen Grüßen\n\n" + "Familie Schröder"
                # mail.send(msg)
                flash('Wir haben dir eine Bestätigungsmail an ' + mail + ' geschickt. '
                      'Kontrolliere auch deinen Spam-Ordner ;-)', 'success')
    return render_template('requestbooking.html'), 200


@app.route('/availability')
def get_availability():
    today = datetime.today()
    year = request.args.get('year', default=today.year, type=int)
    month = request.args.get('month', default=today.month, type=int)
    if month not in range(1, 13):
        return render_template('errorHandling/error.html', message='ValueError: month must be in 1..12 or empty'), 400
    dates = get_month_data(year, month)
    dates = calculate_monthStartDays(dates)
    weeks = calculate_weeks(dates)
    infos = get_Infos(month, year)
    fa_key = os.environ.get('fa_API_KEY')
    return render_template('calendar.html', weeks=weeks, infos=infos, fa_key=fa_key), 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorHandling/404.html'), 404


@app.route('/')
def index():
    return 'Welcome to Availability checker for holiday apartment Haidle.' \
           'Please visit us on ferienwohnung-haidle.de', 200


if __name__ == '__main__':
    app.run()
