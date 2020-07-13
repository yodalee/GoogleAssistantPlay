from flask import Flask, request, jsonify, make_response
import pickledb
import json
import random
import i18n

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
db = pickledb.load('simple.db', False)

# import i18n for translate document
i18n.load_path.append('locales')
i18n.set('file_format', 'json')
i18n.set('fallback', 'en')

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
    language_code = data.get("queryResult").get("languageCode")
    print(language_code)
    i18n.set('locale', language_code)

    action_name = data.get("queryResult").get("intent").get("displayName")
    if action_name == "Default Welcome Intent":
        low = 0
        high = 5
        target = random.randint(low+1, high-1)
        db.set(session, (low, target, high))
        text = i18n.t('guess.welcome', low = str(low), high = str(high))
        print("Response:{}".format(text))
        reply = { "fulfillmentText": text }
        return jsonify(reply)

    elif action_name == "GuessNumber":
        pair = db.get(session)
        guessnum = int(data.get("queryResult").get("parameters").get("number"))
        minnum, target, maxnum = pair
        if guessnum > maxnum or guessnum < minnum:
            text = i18n.t('guess.guess_out', low = str(minnum), high = str(maxnum))
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
                text = i18n.t('guess.guess_unmatch', low = str(minnum), high = str(maxnum))
                db.set(session, (minnum, target, maxnum))

        print("Response:{}".format(text))
        reply = { "fulfillmentText": text }
        return jsonify(reply)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
