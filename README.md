<!--
title: 'AWS Twitch EventSub to Discord Webhook'
description: 'This template takes go-live events from Twitch EventSub, and publishes the events through a Discord webhook.'
layout: Doc
framework: v3
platform: AWS
language: python
authorLink: 'https://github.com/dylmye'
authorName: 'Dylan Myers'
authorAvatar: 'https://avatars1.githubusercontent.com/u/7024578?s=200&v=4'
-->

# Serverless Framework Python Twitch EventSub to Discord Webhook on AWS

This template takes go-live events from Twitch EventSub, and publishes the events through a Discord webhook.

## Usage

### Required Parameters

Set these up in the .env file or pass them as parameters in the monitoring display. Remember that if you are auto-deploying from GitHub etc. your .env file will not be available for the script to read from.

* `DISCORD_WEBHOOK_URL`: This is the URL provided by the Discord webhook you have set up
* `DISCORD_ROLE_ID`: If you want to @everyone when you go live, set this to "everyone", otherwise set it to the ID of the Discord role that should be @'d.
* `TWITCH_USERNAME`: This is your Twitch username for users to click on!

### Deployment

> Make sure to make your .env file following the .env.example file!

```
$ serverless deploy
```

After deploying, you should see output similar to:

```bash
Deploying aws-python-twitch-eventsub-to-discord-webhook to stage dev (us-east-1)

✔ Service deployed to stack aws-python-twitch-eventsub-to-discord-webhook-dev (140s)

endpoint: GET - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/webhook
functions:
  handler: aws-python-twitch-eventsub-to-discord-webhook-dev-webhook (2.3 kB)
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

**Prerequisites:**

* A [Twitch Developer app](https://dev.twitch.tv/console/apps/)
* An API client, like [Postman](https://www.postman.com/downloads/) or [Insomnia](https://insomnia.rest/download)
* 5 minutes of your time

You need to [subscribe your deployment to a Twitch Event](https://dev.twitch.tv/docs/eventsub). For our use case here, we want to subscribe to [`stream.online`](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#streamonline) for a specific channel. Instructions on how to do this are available as [step 7 and step 8 in this guide](https://dylmye.me/2021/03/08/twitch-discord/). The `transport.callback` value should be the `endpoint` from the deploy output above.

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function webhook
```

Which should result in response similar to the following:

```
{
  "statusCode": 200,
  "body": "{\n  \"executed\": False,\n  \"rqid\": \"\"\n}"
}
```

Alternatively, it is also possible to emulate API Gateway and Lambda locally by using `serverless-offline` plugin. In order to do that, execute the following command:

```bash
serverless plugin install -n serverless-offline
```

It will add the `serverless-offline` plugin to `devDependencies` in `package.json` file as well as will add it to `plugins` in `serverless.yml`.

After installation, you can start local emulation with:

```
serverless offline
```

To learn more about the capabilities of `serverless-offline`, please refer to its [GitHub repository](https://github.com/dherault/serverless-offline).

## Credits

This Serverless template is an adaptation of [this Lambda](https://github.com/dylmye/twitch-golive-discord) I created in 2021 - please also see the credits section there

This README is shamelessly adapted from [aws-node-http-api](https://github.com/serverless/examples/tree/v3/aws-node-http-api)'s README, written by [Matthieu Napoli](https://github.com/mnapoli) for Serverless.
