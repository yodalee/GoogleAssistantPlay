from flask import Flask, request, jsonify, make_response
import json

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

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
    action_name = data.get("queryResult").get("intent").get("displayName")
    if action_name == "Default Welcome Intent":
        text = "I have a number between 1 and 50. Can you guess it?"
        print("Response:{}".format(text))
        reply = { "fulfillmentText": text }
        return jsonify(reply)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
