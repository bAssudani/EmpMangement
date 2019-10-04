FROM python:2.7.10

ENV BIND_PORT 5000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./run.py /run.py

EXPOSE $BIND_PORT

CMD [ "python", "/run.py" ]