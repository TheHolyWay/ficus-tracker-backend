import logging
import time
import threading
from app.recommendations.recommendations import DateBasedRecommendation


class RecommendationBackGroundTask:
    def __init__(self, recom, interval=60):
        self.interval = interval
        self.recom = recom

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        from app.models import RecommendationAlarm
        from app import db
        while True:
            alarm = RecommendationAlarm.query.filter_by(task=self.recom.t_id).first()

            if self.recom.check():
                logging.info("Creating alarm!")
                if not alarm:
                    alarm = RecommendationAlarm()
                    alarm.task = self.recom.t_id
                    alarm.message = self.recom.text
                    alarm.severity = self.recom.severity

                    db.session.add(alarm)
                    db.session.commit()
            else:
                if not isinstance(self.recom, DateBasedRecommendation):
                    if alarm:
                        db.session.delete(alarm)
                        db.session.commit()

            time.sleep(self.interval)
