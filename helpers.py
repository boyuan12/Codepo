import requests
import random
import base64
import cloudconvert
import os
import json

cloudconvert.configure(api_key=os.getenv("CLOUDCONVERT_API_KEY"))

def random_word(n=3):
    adjs = requests.get("https://gist.githubusercontent.com/farisj/cc70300356eca8f54c47/raw/c5cbe6dd14eb11b744f9bfe1c1ebcb21fee9ef06/adjectives.txt").text.split("\n")
    nouns = requests.get("https://gist.githubusercontent.com/davidbalbert/ac7b813f498de4a1b02e/raw/d747d58d04a33c13dd9e71b11a3ea2e7f2fa7cdd/nouns.txt").text.split("\n")
    verbs = requests.get("https://gist.githubusercontent.com/farisj/f2ebb73fabfa20dfc40e7fa9de72ddd8/raw/177c42dfd638ed82dac253486a77f7e56fde74ad/verbs.txt").text.split("\n")
    return f"{random.choice(adjs).capitalize()}{random.choice(verbs).capitalize()}{random.choice(nouns).capitalize()}"


def base64_encode(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def base64_decode(base64_message):
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message


def convert_file(original_url, output_file_format):
    job = cloudconvert.Job.create(payload={
        "tasks": {
            'import-my-file': {
                'operation': 'import/url',
                'url': original_url
            },
            'convert-my-file': {
                'operation': 'convert',
                'input': 'import-my-file',
                'output_format': output_file_format,
            },
            'export-my-file': {
                'operation': 'export/url',
                'input': 'convert-my-file'
            }
        }
    })

    export_task_id = job["tasks"][2]["id"]

    res = cloudconvert.Task.wait(id=export_task_id) # Wait for job completion
    file = res.get("result").get("files")[0]
    return file["url"]
