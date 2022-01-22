#                                    ┌───────────────────────────────────────────┐
#                                    │    Copyright (c) 2022 Nikita Paniukhin    │
#                                    │      Licensed under the MIT license       │
#                                    └───────────────────────────────────────────┘
#
# ======================================================================================================================

from PIL import Image
import os

from utils import mkpath


US_IMAGES_PATH = mkpath("../", "api", "US", "images")


def print_dimentions():
    for file in os.listdir(US_IMAGES_PATH):
        image = Image.open(mkpath(US_IMAGES_PATH, file))

        # print(image.size, file)

        # if image.size[0] / image.size[1] == 16 / 9:
        #     print("16/9")

        # elif image.size[0] / image.size[1] == 4 / 3:
        #     print("4/3")

        # else:
        #     print(image.size[0] / image.size[1] * 9)

        image.close()


if __name__ == "__main__":
    print_dimentions()
