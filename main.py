from flask import Flask, request, jsonify, make_response
import pickledb
import json
import random

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
db = pickledb.load('simple.db', False)

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle google action webhook
    :returns: response text
    """
    data = request.get_json(silent=True, force=True)
    print("Request:{}".format(json.dumps(data, indent=2)))

    res = dispatchHandler(data)
    return res

def dispatchHandler(data):
    session = data.get("session")

    action_name = data.get("queryResult").get("intent").get("displayName")
    if action_name == "Default Welcome Intent":
        low = 0
        high = 5
        target = random.randint(low+1, high-1)
        db.set(session, (low, target, high))
        text = "I have a number between {} and {}. Can you guess it?".format(low, high)
        print("Response:{}".format(text))
        reply = { "fulfillmentText": text }
        return jsonify(reply)

    elif action_name == "GuessNumber":
        pair = db.get(session)
        guessnum = int(data.get("queryResult").get("parameters").get("number"))
        minnum, target, maxnum = pair
        if guessnum > maxnum or guessnum < minnum:
            text = "Are you sure? I said a number between {} and {}".format(minnum, maxnum)
        else:
            if guessnum == target:
                event = "User_number_match"
                reply = { "followup_event_input" : { "name" : "User_number_match" } }
                return jsonify(reply)
            else:
                if guessnum < target:
                    minnum = guessnum
                else:
                    maxnum = guessnum
                text = "A number between {} and {}. Keep guess.".format(minnum, maxnum)
                db.set(session, (minnum, target, maxnum))

        print("Response:{}".format(text))
        reply = { "fulfillmentText": text }
        return jsonify(reply)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
