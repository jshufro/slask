import random
import json

P = .005
P_GOOB = .15
MIN_WORDS = 5

replacements = ["mymom", "gooby", "pls", "dolan", "appnexus", "opt"]

def random_response(text, user):
    words = text.split(" ")
    word = random.choice(words)

    responses = []
    responses.append("Very wow")
    responses.append("Yeezy taught me")
    responses.append("You what else is {}? #mymom".format(word))
    responses.append("I agree with {}".format(user))
    responses.append("Sounds good to me, {}".format(user))
    responses.append("I'm proud of you {}".format(user))
    responses.append("That sounds wrong, {}".format(user))
    responses.append("{}, do you even know what you're talking about?".format(user))
    responses.append("{}... just no".format(user))
    for s in replacements:
        responses.append("or... " + text.replace(" " + word + " ", " " + s + " "))

    return random.choice(responses)

def on_message(msg, server):
    text = msg.get("text", "")
    if text.startswith("!"):
        return False

    words = text.split(" ")
    if len(words) < MIN_WORDS:
        return False

    prob = P

    if "goob" in text:
        prob = P_GOOB

    if random.random() < prob:
        response = json.loads(server.slack.api_call("users.info", user=msg["user"]))
        user = response["user"]["profile"]["real_name"]
        return random_response(text, user)
    else:
        return False

