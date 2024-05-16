import logging.handlers
import os
import sys
import json
from flask import Flask, request
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
logger.info('I0002 Preparing vector DB')
status_code = bb.prepare_vectordb('Paris')
logger.info('Vector DB created. Status : ' + status_code)
logger.info('I0003 Creating Langchain')
bot = bb.create_chain()
logger.info('I0004 Langchain created')

@application.route('/', methods=["GET"])
def default():
    return 'OK'


@application.route('/status', methods=["GET"])
def check_status():
    response = {'status' : status_code}
    return json.dumps(response)


@application.route('/chat', methods=["POST"])
def chat():
    question = request.get_json()['message']
    logger.info('I0005 :::  ' + question)

    reply = bot.invoke(question)
    logger.info('I0006 :::  ' + reply)
    response = {'message' : reply}
    return json.dumps(response)



if __name__ == "__main__":
    application.run()