import json
import os

from google.cloud import storage

from utils import mkpath


with open(mkpath(os.path.dirname(__file__), 'gcloud_conf.json'), 'r', encoding='utf-8') as file:
    GCLOUD_CONF = json.load(file)


class GCloud:
    API_URL = 'https://storage.googleapis.com'

    def __init__(self):
        self.storage_client = storage.Client(project=GCLOUD_CONF['project_id'])
        self.bucket = self.storage_client.get_bucket(GCLOUD_CONF['bucket_name'])

    def upload_file(self, file_path: str, bucket_path: str, skip_exists: bool = False):
        blob = self.bucket.blob(bucket_path)
        if skip_exists and blob.exists():
            print(f'Google Cloud: Skipping update of {bucket_path} because it already exists')
            return gcloud_url(bucket_path)

        blob.upload_from_filename(file_path)
        print(f'Google Cloud: File {file_path} uploaded to {bucket_path}')

        return gcloud_url(bucket_path)


def gcloud_url(bucket_path: str):
    return f'{GCloud.API_URL}/{GCLOUD_CONF["bucket_name"]}/{bucket_path}'


if __name__ == '__main__':
    gcloud = GCloud()
    gcloud.upload_file('../api/US/images/2023-12-08.jpg', '2023-12-08.jpg')
