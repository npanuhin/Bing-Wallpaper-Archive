from typing import Any

from threading import Thread, Lock
import requests
import hashlib
import json
import os

from botocore.exceptions import ClientError
import boto3

from system_utils import mkpath, SRC_PATH


TOKEN_PATH = mkpath(SRC_PATH, 'configs/cloudflare_token.json')

with open(mkpath(SRC_PATH, 'configs/cloudflare.json'), 'r', encoding='utf-8') as file:
    R2_CONFIG = json.load(file)


PRINT_LOCK = Lock()


def print_async(*args: Any, **kwargs: Any):
    with PRINT_LOCK:
        print(*args, **kwargs)


class CloudflareR2:
    def __init__(self):
        token_source = os.environ
        if os.path.isfile(TOKEN_PATH):
            with open(TOKEN_PATH) as token_file:
                token_source = json.load(token_file)

        self.account_id = token_source.get('CLOUDFLARE_ACCOUNT_ID')
        access_key_id = token_source.get('CLOUDFLARE_R2_ACCESS_KEY_ID')
        self.api_token = token_source.get('CLOUDFLARE_R2_API_TOKEN')

        if self.account_id is None or access_key_id is None or self.api_token is None:
            raise Exception('Cloudflare token not found, please read src/README')

        secret_access_key = hashlib.sha256(self.api_token.encode('utf-8')).hexdigest()

        self.client = boto3.client(
            service_name='s3',
            endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
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

    def get_bucket_usage(self) -> tuple[int, int] | None:
        if not self.api_token or not self.account_id:
            return None

        url = f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/r2/buckets/{R2_CONFIG["bucket_name"]}/usage'
        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('success'):
                result = data['result']
                return int(result['payloadSize']), int(result['objectCount'])
        except Exception as e:
            print_async(f'Cloudflare API error: {e}')

        return None

    def get_stats(self, prefix: str = '') -> tuple[int, int]:
        total_size = 0
        total_count = 0

        continuation_token = None
        while True:
            params = {
                'Bucket': R2_CONFIG['bucket_name'],
                'Prefix': prefix,
            }
            if continuation_token:
                params['ContinuationToken'] = continuation_token

            response = self.client.list_objects_v2(**params)

            for item in response.get('Contents', []):
                total_size += item['Size']
                total_count += 1

            if not response.get('IsTruncated'):
                break
            continuation_token = response['NextContinuationToken']

        return total_size, total_count


def r2_url(bucket_path: str) -> str:
    return R2_CONFIG['url_base'] + bucket_path


# ---------------------------------------------------- Development -----------------------------------------------------

if __name__ == '__main__':
    storage = CloudflareR2()
    # print(storage.upload_file('../api/US/en.json', 'test/US/en.json', False))
    # print(storage.download_file('test/US/en.json', '../api/US/en.json'))
    # print(storage.delete_folder('anerg.com/'))
