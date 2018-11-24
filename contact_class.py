from peewee import Model, SqliteDatabase, CharField

class Contact(Model):
    name = CharField()
    phone = CharField(primary_key=True)
    address = CharField()

    class Meta:
        database = SqliteDatabase('contacts.db')