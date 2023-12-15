from google.cloud import storage
import json


with open('gcloud_conf.json', 'r', encoding='utf-8') as file:
    GCLOUD_CONF = json.load(file)


def upload_file(file_path: str, bucket_path: str):
    storage_client = storage.Client(project=GCLOUD_CONF['project_id'])

    bucket = storage_client.get_bucket(GCLOUD_CONF['bucket_name'])  # your bucket name

    blob = bucket.blob(bucket_path)
    blob.upload_from_filename(file_path)


def get_url(bucket_path: str):
    return f'https://storage.googleapis.com/{GCLOUD_CONF["bucket_name"]}/{bucket_path}'


if __name__ == '__main__':
    upload_file('../api/US/images/2023-12-08.jpg', '2023-12-08.jpg')
