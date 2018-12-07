import requests
import time
import json
import sqlite3
import binascii
import hmac
import requests

from hashlib import sha1
from datetime import datetime

#################################
# from utils import approval, dbupdate
# approval('35a3b12d-10b7-419d-8d39-784ee71e8212', 'ST7oeEnytbBi/0cZGhEjTBzwzrAeP8ChywUd/CNXuEqVpRYPkImg2fyIRB+UZ86G', 'http://52.3.249.111')

def approval(requestid, signing_key, scalr_url):
    payload = """{"approval_status": "approved", "message": "approved"}"""
    date = httpdate(datetime.utcnow())
    sig = signature(date, payload, signing_key)
    time.sleep(30) # add in other work here
    headers = {
     'Date': date,
     'X-Signature': sig,
    }
    print requestid
    r = requests.post( scalr_url + "/integration-hub/callback/" + requestid, headers=headers, data=payload)
    dbupdate(requestid, "approved")
    return  r.status_code

def httpdate(dt):
     """Return a string representation of a date according to RFC 1123
     (HTTP/1.1).

     The supplied date must be in UTC.

     """
     weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
     month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
              "Oct", "Nov", "Dec"][dt.month - 1]
     return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
         dt.year, dt.hour, dt.minute, dt.second)

def signature(date, body, signing_key):
    return binascii.hexlify(hmac.new(signing_key, body + date, sha1).digest())

def dbupdate(requestid, state):
    conn = sqlite3.connect('/opt/sqlite/db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO approval_table values('" + requestid + "', '" + state + "');")

    conn.commit()
    conn.close()
