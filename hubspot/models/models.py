from datetime import datetime

from mongoengine import (
    connect,
    Document,
    IntField,
    StringField,
    DateTimeField,
    FloatField,
)

connect("hubspot", host="hubspot_demo_mongodb", port=27017)


class CreatedUpdatedDocument(Document):
    meta = {"abstract": True}

    updated_at = DateTimeField(default=datetime.now)
    created_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super(CreateUpdateDocument, self).save(*args, **kwargs)


class User(CreatedUpdatedDocument):
    user_id = IntField(required=True)
    access_token = StringField()
    refresh_token = StringField()
    expires_in = IntField()

    meta = {
        "indexes": [
            {
                "fields": ["user_id"],
                "unique": True,
            }
        ]
    }


class Deal(CreatedUpdatedDocument):
    deal_id = IntField(required=True)
    user_id = IntField(required=True)
    name = StringField()
    stage = StringField()
    close_date = DateTimeField()
    amount = FloatField()
    type = StringField()

    meta = {
        "indexes": [
            {
                "fields": ["deal_id"],
                "unique": True,
            },
            "user_id",
        ]
    }
