import datetime
from abc import abstractmethod

import logging

from app.models import FlowerType


class Recommendation:
    @abstractmethod
    def check(self):
        pass

    @staticmethod
    @abstractmethod
    def create_from_db(**kwargs):
        pass


class DateBasedRecommendation(Recommendation):
    def __init__(self, last_check_date, interval, flower_id):
        self.last_check_date = last_check_date
        self.interval = interval
        self.flower_id = flower_id
        self.next_check_date = datetime.datetime(
            year=self.last_check_date.year + self.interval // 12, month=self.interval % 12 + 1,
            day=15, hour=13)

    def check(self):
        logging.info(f"Checking DateBasedRecommendation for flower {self.flower_id}")
        if datetime.datetime.now() >= self.next_check_date:
            self.last_check_date = datetime.datetime.now()
            self.next_check_date = datetime.datetime(
                year=self.last_check_date.year + self.interval // 12, month=self.interval % 12 + 1,
                day=15, hour=13)
            return True
        else:
            return False


class TransplantationRecommendation(DateBasedRecommendation):
    """ Recommendation for flower transplantation """
    def __init__(self, month, interval, last_transpl, flower_id):
        last_date = datetime.datetime(year=last_transpl, month=month, day=15, hour=13)

        super().__init__(last_date, interval, flower_id)

    @staticmethod
    def create_from_db(flower):
        flower_type = FlowerType.query.filter_by(id=flower.flower_type).first()
        logging.info(f"Initialize task TransplantationRecommendation for flower {flower.id}")
        return TransplantationRecommendation(flower_type.transplantation_month + 1,
                                             flower_type.transplantation_interval,
                                             flower.last_transplantation_year,
                                             flower.id)


class MetricBasedRecommendation:
    pass
