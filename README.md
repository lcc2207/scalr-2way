# 2-way/Approval webhook demo

This webhook will give you an example base webhook to execute code based approvals


# Instance setup.
Execute "bootstrap.sh" on the target install

This will install docker and pull down the approval-webhook repo.

# Update the uwsgi.ini file with your settings

```ini
[uwsgi]
chdir = /opt/approval-webhook
http-socket = 0.0.0.0:5018
wsgi-file = webhook.py
callable = app
workers = 1
master = true
plugin = python
env = SCALR_SIGNING_KEY=scalr_signing_key
env = SCALR_URL=https://demo.scalr.com
```

# Launch
execute 'relaunch.sh'
