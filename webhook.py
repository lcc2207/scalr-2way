#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import abort
from flask import make_response

import string
import json
import logging
import binascii
import dateutil.parser
import os
import requests
import sqlite3

from requests.exceptions import ConnectionError
from hashlib import sha1
from datetime import datetime

# inlude files
from validate import validate_request
from utils import approval, dbupdate

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://redis:6379')

conn = redis.from_url(redis_url)

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Configuration variables
SCALR_SIGNING_KEY = os.getenv('SCALR_SIGNING_KEY', '')
SCALR_URL = os.getenv('SCALR_URL', '')

for var in ['SCALR_SIGNING_KEY', 'SCALR_URL']:
    logging.info('Config: %s = %s', var, globals()[var] if 'PASS' not in var else '*' * len(globals()[var]))

@app.route("/")
def list():
   conn = sqlite3.connect('/opt/sqlite/db')
   conn.row_factory = sqlite3.Row

   cur = conn.cursor()
   cur.execute("select * from approval_table")

   rows = cur.fetchall();
   return render_template("list.html",rows = rows)

@app.route('/approval/', methods=['POST'])
def webhook_listener():
    if not validate_request(request, SCALR_SIGNING_KEY):
        abort(403)
    data = json.loads(request.data)
    event = data['eventName']
    logging.info(request.headers)
    requestid = data['requestId']
    owneremail = data['data']['SCALR_FARM_OWNER_EMAIL']
    farmname = data['data']['SCALR_FARM_NAME']
    logging.info(requestid)

    # log pending state and requirest ID to sqlitedb (called from util.py)
    dbupdate(requestid, 'pending', farmname, owneremail)
    # set approval state to pending
    resp = make_response(json.dumps({ "approval_status": "pending", "message": "pending"}), 202)

    # redis (called from util.py)
    q = Queue(connection=conn)
    status = q.enqueue(approval, requestid, SCALR_SIGNING_KEY, SCALR_URL)
    logging.info(status.result)

    return resp

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
