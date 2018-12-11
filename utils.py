#!/usr/bin/env python

import time
import sqlite3
import binascii
import hmac
from hashlib import sha1
import requests
import datetime as dt
import redis
from rq import Worker, Queue, Connection

conn = sqlite3.connect('/opt/sqlite/db')
#################################
# from utils import approval, dbupdate
# approval('<requestid>', '<webhookkey>', 'http://scalr_server')

def approval(requestid, signing_key, scalr_url):
    payload = """{"approval_status": "approved", "message": "approved"}"""
    date = dt.datetime.now().strftime('%a %d %b %Y %H:%M:%S') + ' UTC'
    sig = signature(date, payload, signing_key)
    time.sleep(30) # add in other work here
    headers = {
        'Date': date,
        'X-Signature': sig,
        }
    req = requests.post(scalr_url + "/integration-hub/callback/" + requestid,
                        headers=headers, data=payload)
    dbupdate(requestid, "approved", '', '', '')
    return  req.status_code

def signature(date, body, signing_key):
    return binascii.hexlify(hmac.new(signing_key, body + date, sha1).digest())

def dbupdate(requestid, state ,farmname, owneremail, operation):
    c = conn.cursor()
    if state == 'pending':
        if operation == 'farm.approval.launch':
            operation = 'Launch'
        elif operation == 'farm.approval.terminate':
            operation = 'Terminate'

        c.execute("INSERT OR IGNORE INTO approval_table values('" + requestid + "', '" + farmname + "', '" + owneremail + "', '" + operation + "', '" + state + "');")
    else:
        c.execute("UPDATE approval_table SET status ='" + state + "'  WHERE id= '" + requestid + "';")

    conn.commit()

def dbrow():
   conn.row_factory = sqlite3.Row
   cur = conn.cursor()
   cur.execute("select * from approval_table order by farmname")
   rows = cur.fetchall()
   return(rows)

def redisqueue(approval, requestid, SCALR_SIGNING_KEY, SCALR_URL):
    #redis connections
    listen = ['high', 'default', 'low']
    redis_url = 'redis://redis:6379'
    conn = redis.from_url(redis_url)
    q = Queue(connection=conn)
    status = q.enqueue(approval, requestid, SCALR_SIGNING_KEY, SCALR_URL)
    return(status.result)
