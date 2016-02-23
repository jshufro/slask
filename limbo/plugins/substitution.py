# substitutions: substitutes text for accualy etc

import logging
import re

logger = logging.getLogger(__name__)

substitutes = {
	'actually': 'accualy'
}

def spit_back_substitution(input_string, regex_string, sub_string):
	#general case of responding to particular words with certain phrases

	regex = re.compile(re.escape(regex_string), re.IGNORECASE)
	response = regex.sub(sub_string, input_string)
	return response

def on_message(msg, server):
    text = msg.get("text", "")

    response = text

    for key in substitutes:
		if (msg["user"] == 'mha'):
			response = spit_back_substitution(response, key, substitutes[key])

    if response != text:
    	return 'Are you sure you didn\'t mean "{0}"?\n'.format(response)
    else:
    	return
