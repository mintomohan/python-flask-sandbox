
import sys
import logging
import logging.handlers
import json
from flask import Flask, request
import bedrock_bot as bb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)

application = Flask(__name__)
app = application
application.logger.addHandler(handler)

status_code = bb.prepare_vectordb('Paris')
bot = bb.create_agent()

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
    reply = bot.invoke(question)
    response = {'message' : reply}
    return json.dumps(response)


if __name__ == "__main__":
    application.run()