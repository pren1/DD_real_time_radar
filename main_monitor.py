'follow target user'
from MongoDB import MongoDB
from util import *

db = MongoDB()
target_name = '空崎そらさき'
'Find latest room info'
latest_room_info = db.latest_room(uname='空崎そらさき')
print(latest_room_info)
print(clear_room_info_format(latest_room_info))


