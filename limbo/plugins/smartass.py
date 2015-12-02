import random
import json

P = .001

replacements = ["mymom", "gooby", "pls", "dolan", "appnexus", "opt"]

def random_response(text, user):
    words = text.split(" ")
    word = random.choice(words)

    responses = []
    responses.append("Very wow")
    responses.append("Yeezy taught me")
    responses.append("You who else is {}? #mymom".format(word))
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

    prob = P

    if "goob" in text:
        prob = .15

    if random.random() < prob:
        response = json.loads(server.slack.api_call("users.info", user=msg["user"]))
        user = response["user"]["profile"]["real_name"]
        return random_response(text, user)
    else:
        return False

