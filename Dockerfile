FROM python:3.10

ADD compscibot/ /run/compscibot/
COPY alembic.ini .env requirements.txt start_bot.sh /run

WORKDIR "/run"

RUN pip install -r requirements.txt
RUN chmod +x start_bot.sh

CMD ["/run/start_bot.sh"]
