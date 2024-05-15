#import bedrock_bot as bb
import os
import json
from flask import Flask

application = Flask(__name__)
app = application

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

@application.route('/ask', methods=["GET"])
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