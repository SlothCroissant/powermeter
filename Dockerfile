FROM python:3.9-alpine

LABEL Maintainer="SlothCroissant"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apk add --no-cache gcc
RUN apk --update add --virtual build-dependencies libffi-dev build-base 
RUN pip install -r requirements.txt 
RUN apk del build-dependencies
COPY . .

CMD [ "python3",  "main.py"]