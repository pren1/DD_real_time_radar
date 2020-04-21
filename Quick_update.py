import threading, time
from MongoDB import MongoDB

class Quick_update(object):
    def __init__(self, update_rank_list):
        self.db = MongoDB(update_rank_list=update_rank_list)
        self.target_dict = {}
        # print('Update once when initialized & take a look at time')
        start_time = time.time()
        self.whole_data_bundle()
        self.period_seconds = int(time.time() - start_time) * 2
        # print("--- %s seconds ---" % (self.period_seconds))

    def begin_update_data_periodically(self):
        timerThread = threading.Thread(target=self.timer_func)
        timerThread.start()

    def timer_func(self):
        next_call = time.time()
        while True:
            # print(f"update data at: {datetime.datetime.now()}")
            start_time = time.time()
            self.whole_data_bundle()
            self.period_seconds = int(time.time() - start_time) * 2
            # print("--- %s seconds ---" % (self.period_seconds))
            next_call = next_call + self.period_seconds
            time.sleep(max(next_call - time.time(), 1))

    def whole_data_bundle(self):
        self.target_dict = self.db.get_updated_server_info()
        # print(self.target_dict)

if __name__ == '__main__':
    data_updater = Quick_update(update_rank_list=False)
    data_updater.begin_update_data_periodically()