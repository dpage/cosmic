from PIL import Image
import numpy as np
import json
import os

FOLDER = 'christmas/images'


# From: https://stackoverflow.com/a/35859141
def remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im


def convert_image(filename):
    raw = Image.open(os.path.join(FOLDER, filename), mode='r')
    raw = remove_transparency(raw, (0, 0, 0))
    raw = raw.convert('RGB', colors=8)

    image = np.array(raw)

    image = image.tolist()

    json.dump(image, open(os.path.join(FOLDER, filename[:-4] + '.json'), 'w'),
              separators=(',', ':'),
              sort_keys=True,
              indent=0)


for image in os.listdir(FOLDER):
    # check if the image ends with png
    if image.endswith('.png') or image.endswith('.jpg'):
        print(f'Converting {image}...')
        convert_image(image)


