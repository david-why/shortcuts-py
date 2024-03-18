import argparse
from typing import IO

import requests

ap = argparse.ArgumentParser()
ap.add_argument('link')
ap.add_argument('output', type=argparse.FileType('wb'))
args = ap.parse_args()
link: str = args.link
output: IO[bytes] = args.output

if not link.startswith('https'):
    shortcut_id = link
else:
    shortcut_id = link.split('/')[-1]

data = requests.get(
    f'https://www.icloud.com/shortcuts/api/records/{shortcut_id}'
).json()

shortcut_url = data['fields']['shortcut']['value']['downloadURL']

with output:
    output.write(requests.get(shortcut_url).content)
