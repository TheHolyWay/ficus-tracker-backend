import datetime
from abc import abstractmethod, ABC

import logging

from app.models import FlowerType


class Recommendation(ABC):
    def __init__(self, t_id, text, severity=2):
        self.text = text
        self.severity = severity
        self.t_id = t_id

    @abstractmethod
    def check(self):
        pass

    @staticmethod
    @abstractmethod
    def create_from_db(**kwargs):
        pass


class DateBasedRecommendation(Recommendation):
    def __init__(self, t_id, last_check_date, interval, flower_id, text, severity=2):
        super().__init__(t_id, text, severity)

        self.last_check_date = last_check_date
        self.interval = interval * 12
        self.flower_id = flower_id
        self.next_check_date = datetime.datetime(
            year=self.last_check_date.year + self.interval // 12, month=self.interval % 12 + 1,
            day=15, hour=13)

    def check(self):
        logging.info(f"Checking DateBasedRecommendation for task: {self.t_id}")
        logging.info(f"Current date: {datetime.datetime.now()}")
        logging.info(f"Next check date: {self.next_check_date}")
        if datetime.datetime.now() > self.next_check_date:
            logging.info(f"Triggered")
            self.last_check_date = datetime.datetime.now()
            self.next_check_date = datetime.datetime(
                year=self.last_check_date.year + self.interval // 12, month=self.interval % 12 + 1,
                day=15, hour=13)
            return True
        else:
            return False


class TransplantationRecommendation(DateBasedRecommendation):
    """ Recommendation for flower transplantation """
    def __init__(self, t_id, month, interval, last_transpl, flower_id, flower_name):
        last_date = datetime.datetime(year=last_transpl, month=month, day=15, hour=13)
        mes = f"Пора пересадить цветок {flower_name}!"

        super().__init__(t_id, last_date, interval, flower_id, mes)

    @staticmethod
    def create_from_db(t_id, flower):
        flower_type = FlowerType.query.filter_by(id=flower.flower_type).first()
        logging.info(f"Initialize task TransplantationRecommendation for task: {t_id}")
        return TransplantationRecommendation(t_id,
                                             flower_type.transplantation_month + 1,
                                             flower_type.transplantation_interval,
                                             flower.last_transplantation_year,
                                             flower.id,
                                             flower.name)


class MetricBasedRecommendation:
    pass
