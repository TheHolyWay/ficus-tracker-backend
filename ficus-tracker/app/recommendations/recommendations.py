import datetime
from abc import abstractmethod
from app.models import Flower, FlowerType


class Recommendation:
    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def create_from_db(self, **kwargs):
        pass


class DateBasedRecommendation:
    def __init__(self, last_check_date, interval):
        self.last_check_date = last_check_date
        self.interval = interval
        self.next_check_date = datetime.datetime(
            year=self.last_check_date.year + self.interval // 12, month=self.interval % 12 + 1,
            day=15, hour=13)

    def check(self):
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
    def __init__(self, month, interval, last_transpl):
        last_date = datetime.datetime(year=last_transpl, month=month, day=15, hour=13)

        super().__init__(last_date, interval)

    def create_from_db(self, flower):
        flower_type = FlowerType.query.filter_by(id=flower.flower_type).first()
        return self.__init__(flower_type.transplantation_month + 1,
                             flower_type.transplantation_interval,
                             flower.last_transplantation_year)


class MetricBasedRecommendation:
    pass
