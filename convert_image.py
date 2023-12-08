from PIL import Image
import numpy as np
import json

image_name = 'pgconfeu'

raw = Image.open(f'{image_name}.png', mode='r').convert('RGB', colors=8)

raw.thumbnail((32, 32))

image = np.array(raw)

image = image.tolist()
json.dump(image, open(f'{image_name}.json', 'w'),
          separators=(',', ':'),
          sort_keys=True,
          indent=0)
