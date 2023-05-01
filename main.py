from flask import Flask, request, render_template, flash, redirect, url_for
from datetime import datetime, timedelta
from icalendar import Calendar
import google.cloud.logging
import requests
import re
import os

import mailing

app = Flask(__name__)
app.secret_key = os.environ.get('Flask_Secret_Key_FEWO')

BOOKIPY_URL = 'https://api.bookiply.com/pmc/rest/apartments/43146778/ical.ics?key=' + os.environ.get('BOOKIPLY_API_Key')
fa_key = os.environ.get('fa_API_KEY')
# booked_dates may could occur errors, if two requests at same time?!
# used in get_month_data (read and write) and calculate_monthStartDays (write)
booked_dates = []

logClient = None


def logger():
    global logClient
    if not app.debug and not logClient:
        logClient = google.cloud.logging.Client()
        logClient.setup_logging()
    return app.logger


def getICALCalendar():
    response = requests.get(BOOKIPY_URL)
    content = response.text
    cal = Calendar.from_ical(content)
    return cal


def get_month_data(year, month):
    # Verarbeiten Sie den Inhalt der iCal-Datei
    cal = getICALCalendar()
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


def checkIfFlatIsAvailable(startDate, endDate):
    cal = getICALCalendar()
    # iterate through all events in requested period
    for event in cal.walk('VEVENT'):
        start = datetime.strptime(str(event.get('DTSTART').dt), '%Y-%m-%d')
        end = datetime.strptime(str(event.get('DTEND').dt), '%Y-%m-%d')
        if start < startDate < end:
            return False
        if start < endDate < end:
            return False
        if startDate <= start and endDate >= end:
            return False
    return True


def priceText(price_flat, price_tax, days):
    return "Der voraussichtliche Preis für " + str(days) + " Tage: " + str(price_flat) + "€\nKurtaxe: " \
        + str(price_tax) + "€\nGesamtpreis: " + str(float(price_flat) + float(price_tax)) + "€"


@app.route('/requestbooking', methods=['GET', 'POST'])
def requestBooking():
    if request.method == 'POST':
        postValid = True
        mail = request.form['email']
        gender = request.form['gender']
        firstName = request.form['first-name']
        lastName = request.form['last-name']
        startDate = request.form['start-date']
        endDate = request.form['end-date']
        adults = int(request.form['adults'])
        children = int(request.form['children'])
        sendConfirmation = "confirmation-mail" in request.form
        message = request.form['message']
        data_protection = "data-protection" in request.form
        price_flat = request.form['price-flat']
        price_tax = request.form['price-tax']
        # get children ages
        childrenAges = []
        for i in range(1, children + 1):
            childrenAges.append(int(request.form['age-' + str(i)]))

        # check if datefields are empty otherwise an error occurs in the next step
        if not startDate or not endDate:
            flash('Bitte gebe ein Datum für Buchungsbeginn/Buchungsende ein!', 'error')
            return render_template('requestbooking.html', fa_key=fa_key), 200
        startDate = datetime.strptime(startDate, '%Y-%m-%d')
        endDate = datetime.strptime(endDate, '%Y-%m-%d')
        # check if data are valid
        if not mail:
            flash('Bitte geben Sie eine gültige E-Mail-Adresse ein,'
                  ' über die wir eine Buchung bestätigen können', 'error')
            postValid = False
        if not firstName:
            flash('Bitte geben Sie Ihren Vornamen ein', 'error')
            postValid = False
        if not lastName:
            flash('Bitte geben Sie Ihren Nachnamen ein', 'error')
            postValid = False

        # check dates
        today = datetime.today()
        if (startDate < today.replace(hour=0, minute=0, second=0, microsecond=0)) or \
                (endDate < today.replace(hour=0, minute=0, second=0, microsecond=0)):
            flash('Ihre Buchungsanfrage liegt in der Vergangenheit. '
                  'Wir können viele Wünsche erfüllen aber leider keine Zeitreisen ermöglichen. '
                  'Wählen Sie einen Buchungszeitraum in der Zukunft aus. ', 'error')
            postValid = False
        elif startDate > endDate:
            flash('Ihr gewähltes Buchungsende liegt vor dem Buchungsbeginn. '
                  'Bitte wählen Sie einen korrekten Zeitraum aus.', 'error')
            postValid = False
        elif startDate == endDate:
            flash('Buchungsbeginn und Buchungsende sind am gleichen Tag gewählt. '
                  'Bitte wählen Sie korrekten Zeitraum aus.', 'error')
            postValid = False
        # check if start day is a saturday
        elif startDate.weekday() != 5:
            flash('Wir vermieten nur wochenweise von Samstag - Samstag. '
                  'Bitte wählen Sie einen Samstag als Buchungsbeginn!', 'error')
            postValid = False
        # check if end day is a saturday
        elif endDate.weekday() != 5:
            flash('Wir vermieten nur wochenweise von Samstag - Samstag. '
                  'Bitte wählen Sie einen Samstag als Buchungsende!', 'error')
            postValid = False
        # check if flat is already booked
        elif not checkIfFlatIsAvailable(startDate, endDate):
            flash('Die Wohnung ist im von Ihnen gewählte Zeit ist leider bereits gebucht. '
                  'Bitte wählen Sie einen anderen Zeitraum aus.', 'error')
            postValid = False

        # check persons
        if adults + children <= 0:
            flash('Es musst mindestens eine Person anreisen!', 'error')
            postValid = False
        if adults + children > 4:
            flash('Sie können mit maximal drei weiteren Personen anreisen! '
                  'Bitte passen Sie Ihre Personenanzahl an.', 'error')
            postValid = False
        for i in childrenAges:
            if i < 0 or i > 17:
                flash('Bitte geben Sie für jedes Kind ein korrektes Alter an!', 'error')
                postValid = False
                break
        if data_protection is False:
            flash('Bitte bestätigen Sie die Datenschutzerklärung!', 'error')
            postValid = False
        if not price_flat or not price_tax:
            price = "Der voraussichtliche Preis konnte leider nicht ermittelt werden."
        else:
            price = priceText(price_flat, price_tax, (endDate - startDate).days)
        if postValid:
            b = mailing.Booking(mail, gender, firstName, lastName, startDate, endDate, adults, children, message, childrenAges, price)
            # Handle request
            mailing.sendAdminNotification(app, b)
            flash('Vielen Dank für Ihre Buchungsanfrage! '
                  'Wir haben diese erhalten und melden uns schnellstmöglich bei Ihnen.', 'success')
            if sendConfirmation:
                # send submit mail
                mailing.sendUserNotification(app, b)
                flash('Wir haben Ihnen eine Bestätigungsmail an ' + mail + ' geschickt. '
                      'Bitte auch den Spam-Ordner kontrollieren ;-)', 'success')
            return redirect(url_for('requestBooking'))  # redirect to clear request data
    return render_template('requestbooking.html', fa_key=fa_key), 200


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
    return render_template('calendar.html', weeks=weeks, infos=infos, fa_key=fa_key), 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorHandling/404.html'), 404


@app.route('/')
def index():
    return render_template('index.html'), 200


if __name__ == '__main__':
    app.run()
