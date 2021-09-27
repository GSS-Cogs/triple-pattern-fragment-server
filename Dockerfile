FROM node:alpine3.11

# Required by node for hdt package, believe it or not
#RUN yarn add python3
#RUN yarn install

COPY ./hdt/* ./data/
COPY config.json .

RUN npm install -g @ldf/server
