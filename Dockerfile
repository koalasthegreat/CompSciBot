FROM python:3.10

ADD compscibot/ /run/compscibot/
COPY alembic.ini .env requirements.txt /run

WORKDIR "/run"

RUN pip install -r requirements.txt

CMD ["python3", "-m", "compscibot"]
