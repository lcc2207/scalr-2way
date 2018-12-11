FROM debian:jessie-slim
MAINTAINER Scalr <@scalr.com>

RUN apt-get update && \
    apt-get install -y --no-install-recommends python python-dev python-pip uwsgi uwsgi-plugin-python sqlite3 && \
    groupadd uwsgi && \
    useradd -g uwsgi uwsgi

COPY ./requirements.txt /opt/approval-webhook/

RUN pip install -r /opt/approval-webhook/requirements.txt

COPY . /opt/approval-webhook

EXPOSE 5018

CMD ["/usr/bin/uwsgi", "--ini", "/opt/approval-webhook/uwsgi.ini", "--logto2", "/var/log/webhook/webhook.log"]
