import requests
import json
from typing import Tuple


async def get_public_seed() -> Tuple[int, str] | None:
    api_url = 'https://eos.greymass.com'
    response = requests.get(api_url + '/v1/chain/get_info')
    if not response.status_code == 200:
        return

    head_block_num = response.json().get('head_block_num')
    if not head_block_num:
        return

    eos_block = head_block_num + 1 # Todo

    response = requests.post(f'{api_url}/v1/chain/get_block_info',
                             data=json.dumps({"block_num": eos_block}))
    if not response.status_code:
        return

    block_info = response.json().get('id')
    if not block_info:
        return
    return eos_block, block_info
