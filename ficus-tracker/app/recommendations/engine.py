import time
import threading

from app.models import RecommendationAlarm
from app import db


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
                alarm = RecommendationAlarm.query.filter_by(task=self.recom.t_id).first()
                if not alarm:
                    alarm = RecommendationAlarm()
                    alarm.task = self.recom.t_id
                    alarm.message = self.recom.text
                    alarm.severity = self.recom.severity

                    db.context.add(alarm)
                    db.context.commit()

            time.sleep(self.interval)
