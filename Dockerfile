FROM python:3.12.0-alpine

RUN apk add --no-cache git
RUN git clone https://github.com/tsi-unito/UnitoBOT /usr/src/app

WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt


CMD [ "python", "./bot.py" ]