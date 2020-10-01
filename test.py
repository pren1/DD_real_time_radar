import requests
import pprint
import pdb

contents = requests.get('https://api.vtbs.moe/v1/info').json()
result = []
for single in contents:
    if single['roomid'] == 7688602:
        pdb.set_trace()
    if single['liveStatus'] == 1:
        result.append(single['roomid'])
pdb.set_trace()
pprint.pprint(result)
