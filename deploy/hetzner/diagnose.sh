#!/bin/bash
# Tijdelijk diagnostisch script. Verwijder na gebruik.

echo "=== DATABASE_URL en resolved URI ==="
cd /usr/home/drf93y/handbalsint-truiden
/usr/home/drf93y/virtualenvs/handbalclub_v2/bin/python -c "
import config
print('DATABASE_URL env:', repr(__import__('os').environ.get('DATABASE_URL')))
print('ProductionConfig URI:', config.ProductionConfig.SQLALCHEMY_DATABASE_URI)
"

echo
echo "=== volledige app-import (zelfde als app.fcgi) ==="
/usr/home/drf93y/virtualenvs/handbalclub_v2/bin/python -c "
import sys
sys.path.insert(0, '/usr/home/drf93y/handbalsint-truiden')
from wsgi import app as flask_app
print('IMPORT OK:', flask_app)
"

echo
echo "=== test: een echt request simuleren via Flask test client ==="
/usr/home/drf93y/virtualenvs/handbalclub_v2/bin/python -c "
import sys
sys.path.insert(0, '/usr/home/drf93y/handbalsint-truiden')
from wsgi import app as flask_app
client = flask_app.test_client()
resp = client.get('/')
print('Status:', resp.status_code)
print('Body (eerste 300 tekens):', resp.get_data(as_text=True)[:300])
"

echo
echo "=== app.fcgi rechtstreeks uitvoeren (zoals Apache/mod_fcgid dat doet) ==="
cd /usr/home/drf93y/public_html/handbalclub-public
timeout 5 ./app.fcgi 2>&1
echo "exit code: $?"
