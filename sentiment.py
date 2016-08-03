from __future__ import division
from __future__ import print_function
import base64
import io
import re
import sys

from googleapiclient import discovery
from PIL import Image


API_KEY = 'AIzaSyDWmb6AEyzdF-QfcZL4gwEI5FEffQhckJc'

RECOMMENDED_WIDTH = 640
RECOMMENDED_HEIGHT = 480


def encode_image(filename):
    with open(filename, 'rb') as image_file:
        image = Image.open(image_file)
        image_width, image_height = image.size
        scaling_factor = min(
            RECOMMENDED_WIDTH / image_width,
            RECOMMENDED_HEIGHT / image_height)
        if scaling_factor < 1.0:
            size = (
                int(image_width * scaling_factor),
                int(image_height * scaling_factor)
            )
            image = image.resize(size, resample=Image.BICUBIC)
            output = io.BytesIO()
            image.save(output, format='PNG')
            image_content = output.getvalue()
        else:
            image_file.seek(0)
            image_content = image_file.read()
    return base64.b64encode(image_content)


def cleanup_text(text):
    text = re.sub(r'net\n(memegene)?ra(tor)?', '', text)
    text = re.sub(r'memegenerator\.net', '', text)
    text = ' '.join(text.split())
    return text


def annotate(service, image_file, max_labels=10):
    image_content = encode_image(image_file)
    request = service.images().annotate(body={
        'requests': [{
            'image': {'content': image_content.decode('utf-8')},
            'features': [{
                'type': 'LABEL_DETECTION',
                'maxResults': max_labels,
            }, {
                'type': 'TEXT_DETECTION',
                'maxResults': 1,
            }],
        }],
    })
    response = request.execute()['responses'][0]
    annotations = response['labelAnnotations']
    labels = [annotation['description'] for annotation in annotations]
    if 'textAnnotations' in response:
        text = cleanup_text(response['textAnnotations'][0]['description'])
    else:
        text = None
    return labels, text


vision_service = discovery.build('vision', 'v1', developerKey=API_KEY)
labels, text = annotate(vision_service, sys.argv[1])
print(' - '.join(labels))
print(text)
