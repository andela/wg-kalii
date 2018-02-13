FROM python:3.6

MAINTAINER collins.abitekaniza@andela.com

WORKDIR /app

COPY . /app

EXPOSE 8000

RUN apt-get -y update && \
      apt-get install -y nodejs npm && \
      npm install bower

RUN pip install -r requirements.txt

RUN invoke create_settings \
         --settings-path ~/.config/wger/settings.py

ENTRYPOINT invoke bootstrap_wger \
         --settings-path ~/.config/wger/settings.py \
         --no-start-server && \
         invoke start_wger --address 0.0.0.0 --port 8000

