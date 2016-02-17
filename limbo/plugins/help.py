"""!help [<command>] prints help on all commands if no command given, or a specific command"""

import re

def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!help( .*)?", text)
    if not match:
        return

    helptopic = match[0].strip()
    if helptopic:
        return server.hooks["extendedhelp"].get(helptopic,
                "No help found for {0}".format(helptopic))
    else:
        # we want to flatten the docs to be line by line rather than plugin by plugin.
        list_of_lists_of_help_docs = [val.split('\n') for val in server.hooks["help"].values()]
        flattened = [ele for sublist in list_of_lists_of_help_docs for ele in sublist]
        # sort and return.
        return "\n".join(sorted(flattened))
