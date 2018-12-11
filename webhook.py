#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import abort
from flask import make_response
from flask import render_template

import string
import json
import logging
import os

# inlude files
from validate import validate_request
from utils import approval, dbupdate, dbrow, redisqueue

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Configuration variables
SCALR_SIGNING_KEY = os.getenv('SCALR_SIGNING_KEY', '')
SCALR_URL = os.getenv('SCALR_URL', '')

for var in ['SCALR_SIGNING_KEY', 'SCALR_URL']:
    logging.info('Config: %s = %s', var, globals()[var] if 'PASS' not in var else '*' * len(globals()[var]))

@app.route("/")
def list():
   rows = dbrow()
   return render_template("list.html",rows = rows)

@app.route('/approval/', methods=['POST'])
def webhook_listener():
    if not validate_request(request, SCALR_SIGNING_KEY):
        abort(403)
    data = json.loads(request.data)
    event = data['eventName']
    requestid = data['requestId']
    owneremail = data['data']['SCALR_FARM_OWNER_EMAIL']
    farmname = data['data']['SCALR_FARM_NAME']
    operation = data['operation']
    logging.info(requestid)

    # log pending state and requirest ID to sqlitedb (called from util.py)
    dbupdate(requestid, 'pending', farmname, owneremail, operation)
    # set approval state to pending
    resp = make_response(json.dumps({ "approval_status": "pending", "message": "pending"}), 202)
    # redis (called from util.py)
    status = redisqueue(approval, requestid, SCALR_SIGNING_KEY, SCALR_URL)
    logging.info(status)
    return resp

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
