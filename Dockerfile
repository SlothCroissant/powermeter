FROM python:3.10.7-alpine

LABEL Maintainer="SlothCroissant"

WORKDIR /src

COPY . .
RUN apk add --no-cache gcc
RUN apk --update add --virtual build-dependencies libffi-dev build-base 
RUN pip install -r requirements.txt 
RUN apk del build-dependencies

CMD [ "gunicorn", "-b", "0.0.0.0:5000", "wsgi:app"]
