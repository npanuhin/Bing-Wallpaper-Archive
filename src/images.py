from hashlib import sha256

from PIL import Image


CHUNK_SIZE = 2 ** 20 * 10  # 10 MB


def get_hash(path: str) -> str:
    result = sha256()
    with open(path, 'rb') as file_to_hash:
        while chunk := file_to_hash.read(CHUNK_SIZE):
            result.update(chunk)
    return result.hexdigest()


def compare_images(path1: str, path2: str) -> bool:
    with open(path1, 'rb') as local_file, open(path2, 'rb') as cloud_file:
        while local_chunk := local_file.read(CHUNK_SIZE):
            cloud_chunk = cloud_file.read(CHUNK_SIZE)
            if local_chunk != cloud_chunk:
                return False
        else:
            if cloud_file.read(CHUNK_SIZE):
                return False
    return True


def compare_image_pixels(path: bytes, path2: bytes) -> bool:
    return Image.open(path).tobytes() == Image.open(path2).tobytes()


# ---------------------------------------------------- Development -----------------------------------------------------

if __name__ == '__main__':
    hashes = {
        # '2023-12-26': get_hash('2023-12-26.jpg')
    }

    with open('output.txt', 'w') as file:
        for key, value in hashes.items():
            file.write(f'{key}:{str(value)}\n')
