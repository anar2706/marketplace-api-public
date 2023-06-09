import os
import json
from peewee import *
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin
from application.helpers.core import load_environment
from playhouse.mysql_ext import JSONField


if not os.environ.get('MYSQL_DB'):
    load_environment()

class RetryMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    _instance = None
 
    @staticmethod
    def get_db_instance():
    
        if not RetryMySQLDatabase._instance:
            RetryMySQLDatabase._instance = RetryMySQLDatabase(
                    os.environ['MYSQL_DB'],
                    max_connections=None,
                    stale_timeout=300,
                    user=os.environ['MYSQL_USER'],
                    password=os.environ['MYSQL_PASS'],
                    host=os.environ['MYSQL_HOST'],
                    port=int(os.environ['MYSQL_PORT']),
                    charset='utf8mb4'
                )

        return RetryMySQLDatabase._instance


db = RetryMySQLDatabase.get_db_instance()

class BaseModel(Model):
    class Meta:
        database = db

class Attributes(BaseModel):
    created = IntegerField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'attributes'

class Buyers(BaseModel):
    created = IntegerField(null=True)
    data = JSONField(null=True)  # json

    class Meta:
        table_name = 'buyers'

class Categories(BaseModel):
    created = IntegerField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'categories'

class Certificates(BaseModel):
    created = IntegerField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'certificates'

class ContactUs(BaseModel):
    company = CharField(null=True)
    created = IntegerField(null=True)
    email = CharField(null=True)
    message = TextField(null=True)
    name = CharField(null=True)
    phone = CharField(null=True)
    surname = CharField(null=True)

    class Meta:
        table_name = 'contact_us'

class ContactHistory(BaseModel):
    created = IntegerField(null=True)
    email = CharField(null=True)
    message = TextField(null=True)
    name = CharField(null=True)
    phone = CharField(null=True)
    product_id = IntegerField(null=True)
    seller_id = CharField(null=True)
    surname = CharField(null=True)

    class Meta:
        table_name = 'contact_history'

class Countries(BaseModel):
    code = CharField(null=True)
    continent = CharField(null=True)
    created = IntegerField(null=True)
    name = CharField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = CharField(null=True)
    zone_id = CharField(null=True)

    class Meta:
        table_name = 'countries'

class EmailTemplates(BaseModel):
    created = IntegerField(null=True)
    html = TextField(null=True)
    language = CharField(null=True)
    plain = TextField(null=True)
    subject = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'email_templates'

class Faq(BaseModel):
    answer = CharField(null=True)
    created = IntegerField(null=True)
    language = CharField(null=True)
    question = CharField(null=True)
    question_id = IntegerField(null=True)

    class Meta:
        table_name = 'faq'

class FavoriteSellers(BaseModel):
    company_id = IntegerField(null=True)
    created = IntegerField(null=True)
    seller_id = IntegerField(null=True)
    user_id = IntegerField(null=True)

    class Meta:
        table_name = 'favorite_sellers'

class NewTable(BaseModel):
    company = CharField(null=True)
    created = IntegerField(null=True)
    email = CharField(null=True)
    message = TextField(null=True)
    name = CharField(null=True)
    phone = CharField(null=True)
    surname = CharField(null=True)

    class Meta:
        table_name = 'new_table'

class ProductCategories(BaseModel):
    category_id = IntegerField(null=True)
    created = CharField(null=True)
    product_id = IntegerField(null=True)

    class Meta:
        table_name = 'product_categories'

class ProductSynonyms(BaseModel):
    created = IntegerField(null=True)
    name = CharField(null=True)
    product_id = IntegerField(null=True)
    product_name = CharField(null=True)
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'product_synonyms'

class ProductTypes(BaseModel):
    created = IntegerField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'product_types'

class Regions(BaseModel):
    code = CharField(null=True)
    country_id = CharField(null=True)
    created = IntegerField(null=True)
    name = CharField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'regions'

class SellerCertificateTypes(BaseModel):
    code = CharField(null=True)
    created = IntegerField(null=True)
    issuing_date = DateField(null=True)
    name = CharField(null=True)
    number = CharField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'seller_certificate_types'

class SellerProducts(BaseModel):
    created = IntegerField(null=True)
    product_id = IntegerField(null=True)
    seller_id = IntegerField(null=True)

    class Meta:
        table_name = 'seller_products'

class Sellers(BaseModel):
    created = IntegerField(null=True)
    payload = JSONField(null=True)  # json
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'sellers'

class Supplies(BaseModel):
    created = IntegerField(null=True)
    payload = JSONField(null=True)  # json
    seller_id = IntegerField(index=True, null=True)
    source = CharField(null=True)
    src_id = IntegerField(null=True)

    class Meta:
        table_name = 'supplies'

class SupplyAttributes(BaseModel):
    attribute_id = IntegerField(null=True)
    created = CharField(null=True)
    supply_id = IntegerField(null=True)

    class Meta:
        table_name = 'supply_attributes'

class Users(BaseModel):
    company_id = IntegerField(null=True)
    created = IntegerField(null=True)
    email = CharField(null=True, unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    password = CharField(null=True)
    phone = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'users'
