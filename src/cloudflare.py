from typing import Any

from threading import Thread, Lock
import json
import os

from botocore.exceptions import ClientError
import boto3

from utils import mkpath


TOKEN_PATH = mkpath(os.path.dirname(__file__), 'configs/cloudflare_token.json')

with open(mkpath(os.path.dirname(__file__), 'configs/cloudflare.json'), 'r', encoding='utf-8') as file:
    R2_CONFIG = json.load(file)


PRINT_LOCK = Lock()


def print_async(*args: Any, **kwargs: Any):
    with PRINT_LOCK:
        print(*args, **kwargs)


class CloudflareR2:
    def __init__(self):
        if os.path.isfile(TOKEN_PATH):
            with open(TOKEN_PATH) as token_file:
                cloudflare_token = json.load(token_file)
            ACCOUNT_ID = cloudflare_token['CLOUDFLARE_ACCOUNT_ID']
            ACCESS_KEY_ID = cloudflare_token['CLOUDFLARE_ACCESS_KEY_ID']
            SECRET_ACCESS_KEY = cloudflare_token['CLOUDFLARE_SECRET_ACCESS_KEY']
        else:
            ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
            ACCESS_KEY_ID = os.environ.get('CLOUDFLARE_ACCESS_KEY_ID')
            SECRET_ACCESS_KEY = os.environ.get('CLOUDFLARE_SECRET_ACCESS_KEY')

        if None in (ACCOUNT_ID, ACCESS_KEY_ID, SECRET_ACCESS_KEY):
            raise Exception('Cloudflare token not found, please read src/README')

        self.client = boto3.client(
            service_name='s3',
            endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY
        )

    # ----------------------------------------------- Working with files -----------------------------------------------

    def exists(self, bucket_path: str) -> bool:
        try:
            self.client.head_object(Bucket=R2_CONFIG['bucket_name'], Key=bucket_path)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
        return True

    def upload_file(self, file_path: str, bucket_path: str, skip_exists: bool = False) -> str:
        if skip_exists and self.exists(bucket_path):
            print_async(f'Cloudflare R2: Skipping upload of {bucket_path} because it already exists')
            return r2_url(bucket_path)

        self.client.upload_file(file_path, R2_CONFIG['bucket_name'], bucket_path)
        print_async(f'Cloudflare R2: File {file_path} uploaded to {bucket_path}')

        return r2_url(bucket_path)

    def download_file(self, bucket_path: str, file_path: str) -> bool:
        if not self.exists(bucket_path):
            print_async(f'Cloudflare R2: File {bucket_path} not found')
            return False

        self.client.download_file(R2_CONFIG['bucket_name'], bucket_path, file_path)
        print_async(f'Cloudflare R2: File {bucket_path} downloaded to {file_path}')

        return True

    def delete_file(self, bucket_path: str, check_exists: bool = True) -> bool:
        if not check_exists and not self.exists(bucket_path):
            print_async(f'Cloudflare R2: File {bucket_path} not found')
            return False

        self.client.delete_object(Bucket=R2_CONFIG['bucket_name'], Key=bucket_path)
        print_async(f'Cloudflare R2: File {bucket_path} deleted')

        return True

    # ---------------------------------------------- Working with folders ----------------------------------------------

    def delete_folder(self, folder_path: str) -> bool:
        threads = []

        while True:
            response = self.client.list_objects_v2(Bucket=R2_CONFIG['bucket_name'], Prefix=folder_path)
            for item in response.get('Contents', []):
                thread = Thread(target=self.delete_file, args=(item['Key'], False))
                threads.append(thread)
                thread.start()

            while threads:
                threads.pop().join()

            if not response.get('IsTruncated', False):
                break

        print_async(f'Cloudflare R2: Folder {folder_path} deleted')

        return True


def r2_url(bucket_path: str) -> str:
    return R2_CONFIG['url_base'] + bucket_path


# ---------------------------------------------------- Development -----------------------------------------------------

if __name__ == '__main__':
    storage = CloudflareR2()
    # print(storage.upload_file('../api/US/en.json', 'test/US/en.json', False))
    # print(storage.download_file('test/US/en.json', '../api/US/en.json'))
    # print(storage.delete_folder('anerg.com/'))
