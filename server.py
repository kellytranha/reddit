
import os
import flask
import requests
from flask_sqlalchemy import SQLAlchemy
from scrappyreddit import bot_loggin, get_imgs_bot, random_url

# payload = {'recipient': {'id': sender},
#             'message': 'attachment': {'type': 'image',
#                                       'payload': {'url': 'http://68.media.tumblr.com/0f55dffe016b4ddd2779146bcd78316b/tumblr_o5kxnfxxHY1s0jodno1_500.jpg'}}}

FACEBOOK_API_MESSAGE_SEND_URL = (
    'https://graph.facebook.com/v2.6/me/messages?access_token=%s')

app = flask.Flask(__name__)

# TODO: Set environment variables appropriately.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['FACEBOOK_PAGE_ACCESS_TOKEN'] = os.environ[
    'FACEBOOK_PAGE_ACCESS_TOKEN']
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')
app.config['FACEBOOK_WEBHOOK_VERIFY_TOKEN'] = 'myverysecretchatbot'


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    facebook_id = db.Column(db.String, unique=True)
    count_messages = db.Column(db.Integer, default=0)


#Helper functions for the behavior of Groot the bot
def handle_message(message, sender_id):
    """This function deals with all the messages from a user. It has all the logic """

    #Handle the connection to Reddit
    reddit = bot_loggin()
    list_urls = get_imgs_bot(reddit)

    #First query for the user that is taking to the bot
    user = User.query.filter(User.facebook_id == sender_id).first()

    #If there is no user it means that is the first time that the user speaks with Groot. 
    if not user:
        user = User(facebook_id=sender_id)
        db.session.add(user)
        db.session.commit()
        return "Hi I'm Groot the wholesome bot.\n What is your name? "

    #If there is an user but the bot doesn't have a name
    elif not user.username:
        user.username = message
        db.session.add(user)
        db.session.commit()
        return "Hi, %s! Are you having a bad day? Yes or No" % (user.username)

    #If an user is having a bad day ask if want some of the images
    elif "YES" in message or "yes" in message or "Yes" in message:
        number_pictures = len(list_urls)
        return "I have %i wholesome pictures to cheer you up.\n Do you want to see a nice picture? Type: hit" % (number_pictures)

    #If an user want a nice picture send one
    elif "HIT" in message or "hit" in message or "Hit" in message:
        picture_day = random_url(list_urls)
        list_urls.remove(picture_day)
        payload = {'url': picture_day}
        return payload

    elif "NO" in message or "no" in message or "not" in message or "No" in message or "Not" in message or "NOT" in message:
        return "That's the spirit %s! Have a good one!" % (user.username)

    elif user.count_messages == 5:
        user.count_messages = 0
        db.session.merge(user)
        db.session.commit()
        return "I'M GROOT"

    else:
        user.count_messages += 1
        db.session.merge(user)
        db.session.commit()
        return "I'm Groot the wholesome bot."


    return "I'm Groot the wholesome bot.\n Are you having a bad day? Yes or No" 


@app.route('/', methods=['GET', 'POST'])
def fb_webhook():
    """This handler deals with incoming Facebook Messages.
    In this example implementation, we handle the initial handshake mechanism,
    then just echo all incoming messages back to the sender. Not exactly Skynet
    level AI, but we had to keep it short...
    """
    # Handle the initial handshake request.
    if flask.request.method == 'GET':
        if (flask.request.args.get('hub.mode') == 'subscribe' and
            flask.request.args.get('hub.verify_token') ==
            app.config['FACEBOOK_WEBHOOK_VERIFY_TOKEN']):
            challenge = flask.request.args.get('hub.challenge')
            return challenge
        else:
            print 'Received invalid GET request'
            return ''  # Still return a 200, otherwise FB gets upset.

    # Get the request body as a dict, parsed from JSON.
    payload = flask.request.json

    # Handle an incoming message.
    for entry in payload['entry']:
        for event in entry['messaging']:
            if 'message' not in event:
                continue
            message = event['message']
            # Ignore messages sent by us.
            if message.get('is_echo', False):
                continue

            # Be a echo of messages with images.
            if 'sticker_id' in message:
                sender_id = event['sender']['id']
                sticker_id = message["sticker_id"]
                url_sticker = message["attachments"][0]["payload"]["url"]


                request_url = FACEBOOK_API_MESSAGE_SEND_URL % (app.config['FACEBOOK_PAGE_ACCESS_TOKEN'])
                response = requests.post(request_url,
                                    headers={'Content-Type': 'application/json'},
                                    json={'recipient': {'id': sender_id},
                                          'message': {'attachment': {'type': 'image',
                                                                     'payload': {'url': url_sticker}}}})
                if response.status_code != 200:
                    print response.text

            if not 'text' in message:
                continue

            #If the message has text the Bot wants to answer that
            sender_id = event['sender']['id']
            message_text = message['text']
            reply = handle_message(message_text, sender_id)

            if type(reply) == dict:
                request_url = FACEBOOK_API_MESSAGE_SEND_URL % (app.config['FACEBOOK_PAGE_ACCESS_TOKEN'])
                requests.post(request_url,
                          headers={'Content-Type': 'application/json'},
                          json={'recipient': {'id': sender_id},
                                'message': {'attachment': {'type': 'image',
                                                           'payload': reply}}})
            else:
                request_url = FACEBOOK_API_MESSAGE_SEND_URL % (app.config['FACEBOOK_PAGE_ACCESS_TOKEN'])
                requests.post(request_url,
                          headers={'Content-Type': 'application/json'},
                          json={'recipient': {'id': sender_id},
                                'message': {'text': reply}})


    # Return an empty response.
    return ''

if __name__ == '__main__':
    
    DEBUG = "NO_DEBUG" not in os.environ
    PORT = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)

