import json
import urllib3
import os

def lambda_handler(event, context):
    """
    Lambda function handler to handle incoming messages from Telegram, send them to the bot,
    and relay the bot's response back to the user via Telegram.
    
    Parameters:
    - event (dict): The event data passed to the Lambda function.
    - context (LambdaContext): The context object representing the runtime information.

    Returns:
    - dict: A dictionary containing the HTTP status code indicating the function's execution status.
    """

    # Telegram API URL
    telegram_url = 'https://api.telegram.org/bot{}/sendMessage'.format(os.environ['telegram_bot_token'])
    # Bot's endpoint URL
    bot_url = os.environ['bot_url']
    
    try:
        # Extracting message details from the event body
        message_body = json.loads(event['body'])['message']
        user_message = message_body.get('text')  # Extracting user's message
        user_chat_id = message_body['chat']['id']  # Extracting user's chat ID
        
        # Constructing the message to be sent from user to bot
        user_to_bot_msg = '{"message": "' + user_message + '"}'
        
        # Creating a HTTP connection pool manager
        http = urllib3.PoolManager()
        
        try:
            # Sending user's message to the bot
            bot_to_user_msg_res = http.request('POST', bot_url,
                                            headers={'Content-Type': 'application/json'},
                                            body=user_to_bot_msg)
            # Extracting bot's response message
            bot_to_user_msg = json.loads(bot_to_user_msg_res.data)["message"]
        except:
            # Handling errors if bot communication fails
            bot_to_user_msg = "It appears that an error has occurred in the bot. Please wait a moment while we resolve the issue."
        
        # Constructing payload to send bot's response to the user via Telegram
        payload = {'chat_id': user_chat_id,
                    'text': bot_to_user_msg
                  }
        
        # Sending bot's response to the user via Telegram
        r = http.request('POST', telegram_url,
                 headers={'Content-Type': 'application/json'},
                 body=json.dumps(payload))
    except Exception as e:
        # Handling unexpected exceptions
        print(e)
    
    # Always return success response
    return {
        'statusCode': 200
    }
