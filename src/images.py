from hashlib import sha256

from PIL import Image


CHUNKSIZE = 2 ** 20 * 10  # 10 MB


def get_hash(path: str) -> str:
    result = sha256()
    with open(path, 'rb') as file:
        while chunk := file.read(CHUNKSIZE):
            result.update(chunk)
    return result.hexdigest()


def compare_images(path1: str, path2: str) -> bool:
    with open(path1, 'rb') as local_file, open(path2, 'rb') as cloud_file:
        while local_chunk := local_file.read(CHUNKSIZE):
            cloud_chunk = cloud_file.read(CHUNKSIZE)
            if local_chunk != cloud_chunk:
                return False
        else:
            if cloud_file.read(CHUNKSIZE):
                return False
    return True


def compare_image_pixels(path: bytes, path2: bytes) -> bool:
    return Image.open(path).tobytes() == Image.open(path2).tobytes()


# ---------------------------------------------------- Development -----------------------------------------------------

if __name__ == '__main__':
    hashes = {}  # noqa
    hashes['2023-12-26'] = get_hash('2023-12-26.jpg')

    with open('output.txt', 'w') as file:
        for key, value in hashes.items():
            file.write(f'{key}:{str(value)}\n')
