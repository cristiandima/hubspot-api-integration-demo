import json, sys, os

import pika
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
from dateutil.parser import parse

import config
from models import models


def request_deals(deals_url, client_id, token, refresh_url, extra):
    try:
        client = OAuth2Session(client_id, token=token)
        return client.get(deals_url)
    except TokenExpiredError as e:
        token = client.refresh_token(refresh_url, **extra)

    client = OAuth2Session(client_id, token=token)
    return client.get(deals_url)


def sync_deals(user_id, deals):
    print(f"FOR USER {user_id} SAVING {len(deals)} DEALS")
    for deal in deals:
        close_date=deal["properties"].get("closedate")
        amount=deal["properties"].get("amount")
        models.Deal.objects(deal_id=int(deal["id"])).modify(
            upsert=True,
            new=True,
            set__user_id=user_id,
            set__name=deal["properties"].get("dealname"),
            set__stage=deal["properties"].get("dealstage"),
            set__close_date=parse(close_date) if close_date is not None else None,
            set__amount=float(amount) if amount is not None else None,
        )


def sync_user_deals(ch, method, properties, body):
    user_data = json.loads(body)
    user_id = user_data["user"]

    user = models.User.objects.get(user_id=user_id)

    token = {
        "access_token": user.access_token,
        "refresh_token": user.refresh_token,
        "token_type": "Bearer",
        "expires_in": user.expires_in,
    }
    client_id = config.HUB_CLIENT_SECRET
    refresh_url = config.HUB_REFRESH_URI
    extra = {
        "client_id": client_id,
        "client_secret": config.HUB_CLIENT_SECRET,
    }
    r = request_deals(config.DEALS_BASE_URL, client_id, token, refresh_url, extra)

    sync_deals(user_id, r.json()["results"])
    next_page = r.json().get("paging", {}).get("next", {}).get("link", None)
    while next_page is not None:
        r = request_deals(next_page, client_id, token, refresh_url, extra)
        sync_deals(user_id, r.json()["results"])
        next_page = r.json().get("paging", {}).get("next", {}).get("link", None)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="hubspot_demo_rabbitmq")
    )
    channel = connection.channel()

    channel.queue_declare(queue="deals")
    channel.basic_consume(
        queue="deals", on_message_callback=sync_user_deals, auto_ack=True
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
