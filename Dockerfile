FROM ubuntu:latest

# TODO:
# Shouldnt be ubuntu (too big) but need node and python in the image (node hdt has a python dependency)
# and getting either into the alpine image for the other was a pita, went the easy route for now.

USER root

RUN apt-get update
RUN apt install nodejs -y
RUN apt install npm -y

RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt install python3.8 -y

COPY ./hdt/* ./usr/app/data/
COPY config.json ./usr/app/

WORKDIR /usr/app
RUN npm install -g @ldf/server
RUN npm install -g hdt --unsafe-perm

ENV PORT 5000

CMD ["ldf-server",  "/usr/app/config.json", "5000", "4"]
