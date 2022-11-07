try:
  import unzip_requirements
except ImportError:
  pass

import json
import requests
from os import environ
from datetime import datetime

# take a twitch event and publish a discord message
def webhook(event, context):
    DISCORD_WEBHOOK_URL = environ.get("DISCORD_WEBHOOK_URL")
    DISCORD_ROLE_ID = environ.get("DISCORD_ROLE_ID")
    TWITCH_USERNAME = environ.get("TWITCH_USERNAME")

    return_obj = {
        "statusCode": 200,
        "body": json.dumps({ "executed": False })
    }

    # handle different data shape when using
    # aws api gateway vs directly using lambda
    data = event
    if ("body" in data or "stageVariables" in data):
        print("Body is nested in root object, loading body instead...")
        data = json.loads(event["body"]) if type(event["body"]) is str else event["body"]

    # Handle verification challenges
    # See: https://dev.twitch.tv/docs/eventsub/handling-webhook-events#responding-to-a-challenge-request
    if ("challenge" in data):
        # !!! If you are going to verify secret HMAC, add that functionality here. It's omitted here for simplification !!!
        print("Handling challenge: " + data["challenge"])
        return_obj["body"] = data["challenge"]
        return return_obj

    # Catch issues where there's no subscription
    # or the status is not enabled or it's
    # a different type of notification
    if ("subscription" not in data or data["subscription"]["status"] != "enabled" or data["subscription"]["type"] != "stream.online"):
        # see: https://dev.twitch.tv/docs/eventsub/handling-webhook-events#revoking-your-subscription
        if (data["subscription"]["status"] == "authorization_revoked"):
            print("Revoked for reason: authorization_revoked")
            return_obj["body"] = json.dumps({ "executed": False, "error": "revoked: user revoked authorization or changed password", "debug_event_obj": data })
            return return_obj

        if (data["subscription"]["status"] == "user_removed"):
            print("Revoked for reason: user_removed")
            return_obj["body"] = json.dumps({ "executed": False, "error": "revoked: broadcaster account was removed", "debug_event_obj": data })
            return return_obj

        if (data["subscription"]["status"] == "notification_failures_exceeded"):
            print("Revoked for reason: notification_failures_exceeded")
            return_obj["body"] = json.dumps({ "executed": False, "error": "revoked: this webhook took too long to respond", "debug_event_obj": data })
            return return_obj

        print(data["subscription"]["status"])
        return_obj["body"] = json.dumps({ "executed": False, "error": "no subscription in request, or subscription type is incorrect.", "debug_event_obj": data })
        return return_obj

    # We add this to the thumbnail URL to break
    # Discord's caching, so it's always the
    # latest thumbnail from live stream
    cache_buster = str(datetime.utcnow().isoformat(timespec='minutes')).replace('-', '').replace(':', '')

    # Determine what to print based on the value
    # of DISCORD_ROLE_ID
    mention_str = ""

    if (DISCORD_ROLE_ID == "everyone"):
        mention_str = "@everyone, "
    elif (DISCORD_ROLE_ID == "nobody"):
        mention_str = "Hey everyone, "
    else:
        mention_str = '<@&' + DISCORD_ROLE_ID + '>, '

    data = {
        "content": mention_str + TWITCH_USERNAME + " is now live on Twitch! Watch at https://twitch.tv/" + TWITCH_USERNAME,
        "embeds": [
            {
                "author": {
                    "name": TWITCH_USERNAME,
                    "url": "https://twitch.tv/" + TWITCH_USERNAME,
                    "icon_url": "https://avatar.glue-bot.xyz/twitch/" + TWITCH_USERNAME
                },
                "image": {
                    "url": "https://static-cdn.jtvnw.net/previews-ttv/live_user_" + TWITCH_USERNAME + "-720x480.jpg?cache=" + cache_buster
                },
                "footer": {
                    "text": "https://twitch.tv/" + TWITCH_USERNAME,
                    "icon_url": "https://i.imgur.com/p4CqTrc.png"
                },
                "color": 8521140
            }
        ]
    }

    result = requests.post(DISCORD_WEBHOOK_URL, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return_obj["body"] = json.dumps({ "executed": False, "error": "discord webhook returned an error. " + err })
    else:
        return_obj["body"] = json.dumps({ "executed": True })

    return return_obj
