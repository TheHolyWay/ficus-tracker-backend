import datetime
from abc import abstractmethod, ABC

import logging

from sqlalchemy import desc


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


class DateBasedRecommendation(Recommendation, ABC):
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
        # logging.info(f"Current date: {datetime.datetime.now()}")
        # logging.info(f"Next check date: {self.next_check_date}")
        if datetime.datetime.now() > self.next_check_date:
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
        mes = f"Пора пересадить растение '{flower_name}'!"

        super().__init__(t_id, last_date, interval, flower_id, mes)

    @staticmethod
    def create_from_db(**kwargs):
        from app.models import FlowerType
        t_id = kwargs.get('t_id')
        flower = kwargs.get('flower')
        flower_type = FlowerType.query.filter_by(id=flower.flower_type).first()
        logging.info(f"Initialize task TransplantationRecommendation for task: {t_id}")
        return TransplantationRecommendation(t_id,
                                             flower_type.transplantation_month + 1,
                                             flower_type.transplantation_interval,
                                             flower.last_transplantation_year,
                                             flower.id,
                                             flower.name)


class LightMaxProblem(Recommendation):
    def __init__(self, t_id):
        self.t_id = t_id
        from app.models import RecommendationItem, FlowerType, Sensor, Flower, IlluminationType
        task = RecommendationItem.query.filter_by(id=self.t_id).first()
        flower = Flower.query.filter_by(id=task.flower).first()
        self.sensor_id = flower.sensor

        flower_type = FlowerType.query.filter_by(id=flower.flower_type).first()
        ilum = IlluminationType.query.filter_by(id=flower_type.illumination).first()
        self.limit = ilum.max_value

        super().__init__(t_id, f"Слишком много света для растения '{flower.name}'", severity=0)

        logging.info(f"Initialized LightMaxProblem for task {self.t_id} and "
                     f"sensor {self.sensor_id}")

    def check(self):
        logging.info(f"Checking LightMaxProblem for task: {self.t_id} and "
                     f"sensor {self.sensor_id}")
        from app.models import FlowerMetric
        last_data = FlowerMetric.query.filter_by(
            sensor=self.sensor_id).order_by(desc(FlowerMetric.time)).first()
        # logging.info(f"Last data for task LightMaxProblem {self.t_id} and sensor {self.sensor_id} "
        #              f"is {last_data.to_dict()}")

        if last_data:
            if float(last_data.light) > float(self.limit) * 1.05:
                # logging.info(f"LightMaxProblem {self.t_id} triggered")
                return True

        return False

    @staticmethod
    def create_from_db(**kwargs):
        return LightMaxProblem(kwargs.get('t_id'))
