#
# Sending emails
#

import os
from flask import Flask
from flask_mail import Mail, Message  # type: ignore
from threading import Thread
from datetime import datetime

from typing import Optional, Tuple, List

# where to send booking requests
admin_account = os.environ.get('smtp_user')


class Booking:
    def __init__(self, mail, gender, firstName, lastName, startDate, endDate, adults, children, message, childrenAges, price):
        self.mail = mail
        self.gender = gender
        self.firstName = firstName
        self.lastName = lastName
        self.startDate = startDate
        self.endDate = endDate
        self.adults = adults
        self.children = children
        self.bookDate = datetime.today()
        self.message = message
        self.childrenAges = childrenAges
        self.price = price


# ------------------------------------------------------------------------------------------


# def remarksText(b: Booking) -> str:
#     if b.remarks == "":
#         return ""
#     items = b.remarks.split("※")
#     t = "\nNachrichten:\n"
#     for item in items:
#         if item.startswith("✉"):
#             t += " - (Car-ship) %s\n" % item[1:]
#         else:
#             t += " - %s\n" % item
#     return t


def bookingText(b: Booking) -> str:
    s = """Buchungsbeginn:  %s
Buchungsende:    %s
Gebuchte Tage:   %s Tage
Erwachsene: %s
Kinder: %s""" % (
        b.startDate.strftime("%d.%m.%Y"),
        b.endDate.strftime("%d.%m.%Y"),
        (b.endDate - b.startDate).days,
        b.adults,
        b.children
    )
    if b.children > 0:
        s += "\nAlter der Kinder: " % b.childrenAges
        for age in b.childrenAges:
            s += "%s " % age
    if b.message != "":
        s += "\nNachricht: \"%s\"" % b.message
    s += "\n" + b.price
    return s


def mailBottom() -> str:
    return """
Viele Grüße aus Eriskirch
i.A. Frau Haidle

Ferienwohnung Haidle 
Irisstraße 26
88097 Eriskirch

Mobil, WhatsApp: 07541 981750
service@ferienwohnung-haidle.de
www.ferienwohnung-haidle.de
"""


# ------------------------------------------------------------------------------------------


def send_async_email(app: Flask, email: Mail, msg: Message):
    with app.app_context():
        if app.debug:
            print("Sending email: %s" % msg)
        email.send(msg)


def getMail(app: Flask) -> Mail:
    app.config.update(MAIL_SERVER=os.environ.get('smtp_server'),
                      MAIL_PORT=465, MAIL_USE_SSL=True,
                      MAIL_USERNAME=os.environ.get('smtp_user'),
                      MAIL_PASSWORD=os.environ.get('smtp_password'),
                      MAIL_DEFAULT_SENDER=os.environ.get('smtp_user'))
    return Mail(app)


# ------------------------------------------------------------------------------------------


def sendAdminNotification(app: Flask, b: Booking):
    # no admin notifications when in the testing app
    if app.debug:
        print("debug send Mail")
        return
    email = getMail(app)
    msg = Message(
        "Benachrichtigung über Buchungsanfrage von " + b.firstName + " " + b.lastName, recipients=[admin_account]
    )
    extra = ""
    extra += "Möchtest du den Zeitraum bei Bookiply blockieren? Das geht hier:"
    extra += "\n\nhttps://www.bookiply.com/app/calendars/43146778\n"

    msg.body = """Liebe Hanna,
    
%s %s %s hat folgende Buchung angefragt:
%s

%s
Die Bestätigung bzw. Ablehnung der Anfrage schickst du bitte an %s

Liebe Grüße,
Deine Buchungsplattform
""" % (b.gender, b.firstName, b.lastName,
       bookingText(b), extra, b.mail)
    thr = Thread(target=send_async_email, args=[app, email, msg])
    thr.start()


def sendUserNotification(app: Flask, b: Booking):
    # no user notifications when in the testing app
    if app.debug:
        print("debug send user-notif. Mail")
        return
    email = getMail(app)
    msg = Message(
        "Wir haben Ihre Anfrage erhalten", recipients=[b.mail]
    )
    salutation = ""
    if b.gender == "Herr":
        salutation += "Sehr geehrter Herr "
    elif b.gender == "Frau":
        salutation += "Sehr geehrte Frau "
    else:
        salutation += "Guten Tag " + b.firstName + " "
    salutation += b.lastName + ","

    msg.body = """%s
    
Ihre Buchungsanfrage wurde an uns weitergeleitet. Wir werden uns schnellstmöglich bei Ihnen melden.
    
Buchung:
%s

Wenn Sie uns zwischenzeitlich noch etwas Mitteilen möchten Antworten Sie einfach auf diese E-Mail.
%s
""" % (salutation, bookingText(b), mailBottom())
    thr = Thread(target=send_async_email, args=[app, email, msg])
    thr.start()

# ------------------------------------------------------------------------------------------
