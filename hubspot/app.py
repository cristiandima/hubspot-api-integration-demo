import os
import json

import pika
import requests

from flask import Flask, request, redirect, session, render_template
from flask.json import jsonify

import config
from models import models
from errors import errors

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_error_handler(errors.OAuthError, errors.handle_oauth_error)


def pub_deal_sync(user):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="hubspot_demo_rabbitmq")
    )
    channel = connection.channel()
    channel.queue_declare(queue="deals")
    channel.basic_publish(
        exchange="", routing_key="deals", body=json.dumps({"user": user})
    )
    connection.close()


@app.route("/")
def home():
    url = f"https://app.hubspot.com/oauth/authorize?client_id={config.HUB_CLIENT_ID}&redirect_uri={config.HUB_REDIRECT_URI}&scope=contacts"
    return render_template("home.html", url=url)


@app.route("/auth/hubapi", methods=["GET"])
def auth_hubapi():
    code = request.args.get("code")

    data = {
        "grant_type": "authorization_code",
        "client_id": config.HUB_CLIENT_ID,
        "client_secret": config.HUB_CLIENT_SECRET,
        "redirect_uri": config.HUB_REDIRECT_URI,
        "code": code,
    }
    r = requests.post("https://api.hubapi.com/oauth/v1/token", data=data)
    if not r.ok:
        raise errors.OAuthError("Cannot get token from hubapi")

    token_resp = r.json()

    r = requests.get(
        f"https://api.hubapi.com/oauth/v1/access-tokens/{token_resp['access_token']}"
    )
    if not r.ok:
        raise errors.OAuthError("Cannot get user information from hubapi")
    user_resp = r.json()

    models.User.objects(user_id=user_resp["hub_id"]).modify(
        upsert=True,
        new=True,
        set__user_id=user_resp["hub_id"],
        set__access_token=token_resp["access_token"],
        set__refresh_token=token_resp["refresh_token"],
        set__expires_in=token_resp["expires_in"],
    )
    session["user"] = user_resp["hub_id"]
    pub_deal_sync(session["user"])

    return redirect("/deals")


@app.route("/deals", methods=["GET"])
def deals():
    if "user" not in session:
        return redirect("/auth/login")

    deals = models.Deal.objects(user_id=session["user"])

    return render_template("deals.html", deals=deals)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
