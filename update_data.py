import datetime, threading, time
from MongoDB import MongoDB
import pdb
from tqdm import tqdm
import pprint

class update_data(object):
    def __init__(self, update_rank_list):
        self.db = MongoDB(update_rank_list=update_rank_list)
        self.total_rank_list = []
        self.message_room_persentage_dict = {}
        self.man_chart_dict = {}
        self.man_status_dict = {}
        self.radar_dict = {}
        self.huolonglive_tracker = {}

        print('Update once when initialized & take a look at time')
        start_time = time.time()
        self.whole_data_bundle()
        self.period_seconds = int(time.time() - start_time) * 2
        print("--- %s seconds ---" % (self.period_seconds))

    def begin_update_data_periodically(self):
        timerThread = threading.Thread(target=self.timer_func)
        timerThread.start()

    def timer_func(self):
        next_call = time.time()
        while True:
            print(f"update data at: {datetime.datetime.now()}")
            start_time = time.time()
            self.whole_data_bundle()
            self.period_seconds = int(time.time() - start_time) * 2
            print("--- %s seconds ---" % (self.period_seconds))
            next_call = next_call + self.period_seconds
            time.sleep(next_call - time.time())

    def whole_data_bundle(self):
        'Fill in the data bundle'
        'first, calculate rank list'
        self.total_rank_list, mid_list = self.db.find_total_rank()
        self.huolonglive_tracker = self.db.build_huolonglive_tracker()
        'Time to update everything~'
        for uid in tqdm(mid_list):
            self.message_room_persentage_dict[uid] = self.db.build_message_room_persentage(uid)
            self.man_chart_dict[uid] = self.db.build_man_chart(uid)
            self.man_status_dict[uid] = self.db.obtain_man_status(uid)
            self.radar_dict[uid] = self.db.build_radar_chart(uid)
        self.db.build_basic_message_sets()
        print("everything get updated")

    def get_total_message(self, uid):
        # pprint.pprint(self.db.total_message_obtain[uid])
        return {'data': self.db.total_message_obtain[uid], 'roomid_list': list(self.db.total_message_obtain[uid].keys())}

if __name__ == '__main__':
    data_updater = update_data(update_rank_list=False)
    # data_updater.begin_update_data_periodically()
    start_time = time.time()
    data_updater.whole_data_bundle()
    print("--- %s seconds ---" % (time.time() - start_time))