FROM openjdk:8-jre-alpine

RUN apk add --no-cache wkhtmltopdf

ENTRYPOINT [ "wkhtmltopdf" ]

FROM python:3.9.13-slim-buster

WORKDIR /beassist

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN python setup.py

CMD [ "python", "app.py"]