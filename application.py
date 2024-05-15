import bedrock_bot as bb
import os
import json
from flask import Flask
import logging
import urllib3
from logging.handlers import RotatingFileHandler

def remote_log(message):
    print('app.py : ' + message)
    http = urllib3.PoolManager()
    msg_template = os.environ['remote_api_message_template']
    print(msg_template)
    req_body = msg_template.replace('message', message)
    r = http.request('POST', os.environ['remote_api_url'],
                headers={'Content-Type': 'application/json'},
                body=req_body)

remote_log('started..')

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/opt/python/log/application.log', maxBytes=1024,backupCount=5)

application = Flask(__name__)
app = application
application.logger.addHandler(handler)

logger.info('I0001 Initial log')

status_code = 'INITIATED'
'''
status_code = bb.prepare_vectordb('Paris')
bot = bb.create_chain()
'''
@application.route('/', methods=["GET"])
def default():
    return 'OK'


@application.route('/status', methods=["GET"])
def check_status():
    response = {'status' : status_code}
    return json.dumps(response)

'''
@application.route('/chat', methods=["GET"])
def chat():
    reply = bot.invoke('What is the population of Paris?')
    response = {'message' : reply}
    return json.dumps(response)
'''


@application.route('/secret', methods=["GET"])
def check_secret():
    secret = os.environ['secret']
    response = {'secret' : secret}
    return json.dumps(response)




if __name__ == "__main__":
    application.run()