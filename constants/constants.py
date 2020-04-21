"name & description of constants"

MONGODB_LOCAL = "mongodb://localhost:27017/"

DATABASE_NAME = "danmaku_db"

SERVER_INFO_NAME = "server_db"

DANMAKU_THRESHORD = 150

ROOM_DANMAKU_THRESHOLD = 10

MAINDB = "until_200220"
"""
information of every interpretation danmaku (without message)
{
	message:[String]
	message_length:[Int32],
	roomid:[Int32],
	mid:[Int32],
	timestamp[Int64]
}
"""
MID_TABLE_OF = "zz_mid"
"""
danmaku data for a specific interpretation man
{
	message_length:[Int32],
	roomid:[Int32],
	timestamp:[Int64],
	message:[String]
}

"""
ROOM_TABLE_OF = "zz_room"
"""
danmaku data for a specific room
{
	message_length:[Int32],
	mid:[Int32],
	timestamp:[Int64],
	message:[String]
}
"""

MID_INFO = "mid_info"
"""
unique ID & nickname of bilibili user
{
	_id:[Int32],
	man_nick_name:[String]
	danmaku_count:[Int32]
	danmaku_len_count:[Int32]
	danmaku_threshord:[Int32]
}
"""

ROOMID_INFO = "roomid_info"
"""
unique ID & nickname of live room
{
	_id:[Int32],
	room_nick_name:[String]
}
"""

RANKING = "rank_top300"

WORKING_THRESHOLD = 10