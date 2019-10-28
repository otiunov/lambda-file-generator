from google.cloud import storage
from flask import abort
import json
from mimesis.schema import Field, Schema
from mimesis.enums import Gender
from tenacity import *
import os

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


class GoogleStorageContainerSingleton:
    """
        Container for Google Cloud Storage service connections.
        To avoid connection initialization during unit testing.
    """

    __instance = None

    @staticmethod
    def get_instance():
        if not GoogleStorageContainerSingleton.__instance:
            GoogleStorageContainerSingleton()
        return GoogleStorageContainerSingleton.__instance

    def __init__(self):
        if GoogleStorageContainerSingleton.__instance:
            raise Exception("This class is a singleton!")
        else:
            self.storage_client = storage.Client()
            self.bucket = self.init_bucket_object()
            GoogleStorageContainerSingleton.__instance = self

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def init_bucket_object(self):
        return self.storage_client.bucket(os.environ['TARGET_BUCKET'])


@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
def init_blob(filename):
    gs_container = GoogleStorageContainerSingleton.get_instance()
    return gs_container.bucket.blob(filename)


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
    blob = init_blob(filename)
    print('Start data generation')
    data = generate_data(size)
    print('End data generation')
    blob.upload_from_string('\n'.join(data))

    return f'{bucket_name}/{filename} with size: {size} has been created', 200


