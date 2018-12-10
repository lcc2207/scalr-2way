#!/usr/bin/env python

import time
import sqlite3
import binascii
import hmac
from hashlib import sha1
from datetime import datetime
import requests

#################################
# from utils import approval, dbupdate
# approval('<requestid>', '<webhookkey>', 'http://scalr_server')

def approval(requestid, signing_key, scalr_url):
    payload = """{"approval_status": "approved", "message": "approved"}"""
    date = httpdate(datetime.utcnow())
    sig = signature(date, payload, signing_key)
    time.sleep(30) # add in other work here
    headers = {
        'Date': date,
        'X-Signature': sig,
        }
    req = requests.post(scalr_url + "/integration-hub/callback/" + requestid,
                        headers=headers, data=payload)
    dbupdate(requestid, "approved", '', '')
    return  req.status_code

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

def dbupdate(requestid, state ,farmname, owneremail):
    conn = sqlite3.connect('/opt/sqlite/db')
    c = conn.cursor()
    if state == 'pending':
            c.execute("INSERT OR IGNORE INTO approval_table values('" + requestid + "', '" + farmname + "', '" + owneremail + "', '"  + state + "');")
    else:
            c.execute("UPDATE approval_table SET status ='" + state + "'  WHERE id= '" + requestid + "';")

    conn.commit()
    conn.close()
