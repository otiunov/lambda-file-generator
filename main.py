from google.cloud import storage
from flask import abort
import json
from mimesis.schema import Field, Schema
from mimesis.enums import Gender


_ = Field('en')
description = (
     lambda: {
         'id': _('uuid'),
         'name': _('text.word'),
         'version': _('version', pre_release=True),
         'timestamp': _('timestamp', posix=False),
         'owner': {
             'email': _('person.email', key=str.lower),
             'token': _('token_hex'),
             'creator': _('full_name', gender=Gender.FEMALE),
         },
     }
 )
schema = Schema(schema=description)

storage_client = storage.Client()


def generate_data(size):
    record_list = [json.dumps(record) for record in schema.create(iterations=size)]
    return record_list


def handle(request):
    if request.method != 'POST':
        return abort(405)

    request_json = request.get_json()
    bucket_name = request_json['bucket']
    filename = request_json['filename']
    size = int(request_json['size'])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string('\n'.join(generate_data(size)))

    return f'{bucket_name}/{filename} with size: {size} has been created', 200


