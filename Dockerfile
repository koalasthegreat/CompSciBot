FROM python:3.10

WORKDIR /run

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY compscibot/ /run/compscibot/
COPY alembic.ini start_bot.sh /run/

RUN chmod +x start_bot.sh

CMD ["/run/start_bot.sh"]
