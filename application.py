import sys
import logging
import logging.handlers
import json
from flask import Flask, request
import bedrock_bot as bb

# Set up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)

# Initialize the Flask application
application = Flask(__name__)
app = application
application.logger.addHandler(handler)

# Prepare the vector database and create the chatbot agent
status_code = bb.prepare_vectordb('Paris')
bot = bb.create_agent()


# Define the default route
@application.route('/', methods=["GET"])
def default():
    return 'OK'


# Define the status check API
@application.route('/status', methods=["GET"])
def check_status():
    response = {'status' : status_code}
    return json.dumps(response)


# Define the chat API
@application.route('/chat', methods=["POST"])
def chat():
    question = request.get_json()['message']
    reply = bot.invoke(question)
    response = {'message' : reply}
    return json.dumps(response)


# Run the application
if __name__ == "__main__":
    application.run()