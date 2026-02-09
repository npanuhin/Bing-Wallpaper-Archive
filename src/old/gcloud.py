import json
import os

from google.cloud import storage

from images import compare_image_pixels
from system_utils import mkpath


with open(mkpath(os.path.dirname(__file__), 'gcloud_conf.json'), 'r', encoding='utf-8') as file:
    GCLOUD_CONF = json.load(file)


class GCloud:
    API_URL = 'https://storage.googleapis.com'

    def __init__(self):
        self.storage_client = storage.Client(project=GCLOUD_CONF['project_id'])
        self.bucket = self.storage_client.get_bucket(GCLOUD_CONF['bucket_name'])

    def exists(self, bucket_path: str):
        blob = self.bucket.blob(bucket_path)
        return exists_blob(blob)

    def upload_file(self, file_path: str, bucket_path: str, skip_exists: bool = False):
        blob = self.bucket.blob(bucket_path)
        if skip_exists and exists_blob(blob):
            print(f'Google Cloud: Skipping upload of {bucket_path} because it already exists')
            return gcloud_url(bucket_path)

        blob.upload_from_filename(file_path)
        print(f'Google Cloud: File {file_path} uploaded to {bucket_path}')

        return gcloud_url(bucket_path)

    def compare_images(self, file_path: str, bucket_path: str) -> bool:
        blob = self.bucket.blob(bucket_path)
        if not exists_blob(blob):
            raise ValueError(f'Google Cloud: Image {bucket_path} does not exist, cannot compare')

        blob.download_to_filename('_temp.jpg')

        identical = compare_image_pixels(file_path, '_temp.jpg')

        os.remove('_temp.jpg')
        return identical


def exists_blob(blob: storage.Blob):
    return blob.exists()


def gcloud_url(bucket_path: str):
    return f'{GCloud.API_URL}/{GCLOUD_CONF["bucket_name"]}/{bucket_path}'


if __name__ == '__main__':
    gcloud = GCloud()
    # print(gcloud.upload_file('../api/US/images/2023-12-08.jpg', '2023-12-08.jpg'))
    print(gcloud.compare_images('b5ef1f21782d1e99e81c31e01a0e9ef5.jpg', 'US/en/2018-10-14.jpg'))
