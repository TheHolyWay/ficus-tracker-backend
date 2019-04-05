FROM python:3.7.2-slim

MAINTAINER mrVLadOS vladislav.vlasov.dev@gmail.com

WORKDIR /opt/ficus-tracker

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=/opt/ficus-tracker/ficus_tracker.py
ENV DATABASE_URL=${DATABASE_URL}

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

CMD [ "python", "/opt/ficus-tracker/ficus_tracker.py" ]
