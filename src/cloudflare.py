import json
import os

from botocore.exceptions import ClientError
import boto3

from utils import mkpath


TOKEN_PATH = mkpath(os.path.dirname(__file__), 'configs/cloudflare_token.json')

with open(mkpath(os.path.dirname(__file__), 'configs/cloudflare.json'), 'r', encoding='utf-8') as file:
    R2_CONFIG = json.load(file)


class CloudflareR2:
    def __init__(self):
        if os.path.isfile(TOKEN_PATH):
            with open(TOKEN_PATH) as file:
                cloudflare_token = json.load(file)
            self.ACCOUNT_ID = cloudflare_token['CLOUDFLARE_ACCOUNT_ID']
            self.AWS_ACCESS_KEY_ID = cloudflare_token['CLOUDFLARE_AWS_ACCESS_KEY_ID']
            self.AWS_SECRET_ACCESS_KEY = cloudflare_token['CLOUDFLARE_AWS_SECRET_ACCESS_KEY']

        else:
            self.ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
            self.AWS_ACCESS_KEY_ID = os.environ.get('CLOUDFLARE_AWS_ACCESS_KEY_ID')
            self.AWS_SECRET_ACCESS_KEY = os.environ.get('CLOUDFLARE_AWS_SECRET_ACCESS_KEY')

        if None in (self.ACCOUNT_ID, self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY):
            raise Exception('Cloudflare token not found, more info in README')

        self.client = boto3.client(
            service_name='s3',
            endpoint_url=f'https://{self.ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY
        )

    def exists(self, bucket_path: str):
        try:
            self.client.head_object(Bucket=R2_CONFIG['bucket_name'], Key=bucket_path)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
        return True

    def upload_file(self, file_path: str, bucket_path: str, skip_exists: bool = False):
        if skip_exists and self.exists(bucket_path):
            print(f'Cloudflare R2: Skipping upload of {bucket_path} because it already exists')
            return r2_url(bucket_path)

        self.client.upload_file(file_path, R2_CONFIG['bucket_name'], bucket_path)
        print(f'Cloudflare R2: File {file_path} uploaded to {bucket_path}')

        return r2_url(bucket_path)


def r2_url(bucket_path: str):
    return R2_CONFIG["url_base"] + bucket_path


if __name__ == "__main__":
    storage = CloudflareR2()
    print(storage.upload_file('../api/US/en.json', 'test/US/en.json', False))
