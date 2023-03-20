# Availability-calendar for Bookiply rental Appartments
This Python Flask Applikation queries bookings from Bookiply (or each other Booking Platform supports iCal) and output them as a HTML-Calendar

## Development Environment

### Setting up Python:

Install: python3.9 python3.9-dev python3.9-venv

Setting up an isolated environment:
```
python3.9 -m venv venv
```

This sets up everything in the `venv` directory.
Activate it using:
```
source venv/bin/activate
```
Deactivate using
```
deactivate
```

Now you can install packages without affecting other projects or your
global Python installation:
```
pip install -r requirements.txt
```

### Google Cloud Umgebung

See Google documentation: https://cloud.google.com/sdk/docs/downloads-apt-get

Install these packages:
```
google-cloud-sdk-app-engine-python
google-cloud-sdk-app-engine-python-extras
```

Einrichten:
```
gcloud init
```

### Deployment im Google-Datacenter

```
bash deploy.sh
```

Management der App: https://console.cloud.google.com/home/dashboard

App-Engine Dashboard: https://console.cloud.google.com/appengine

Show Log while app run:
```
gcloud app logs tail
```

## Credentials
Credentials for CI Deployment to Google App-Engine and API-Keys for Bookiply and Fontawesome needs to be stored in
Git-Hub secrets
