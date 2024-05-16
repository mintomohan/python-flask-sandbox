import logging.handlers
import os
import sys
import json
from flask import Flask
import logging
import bedrock_bot as bb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
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





if __name__ == "__main__":
    application.run()