import time
import threading


class RecommendationBackGroundTask:
    def __init__(self, recom, interval=60):
        self.interval = interval
        self.recom = recom

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            if self.recom.check():
                pass

            time.sleep(self.interval)
