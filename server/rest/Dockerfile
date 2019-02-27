FROM node:11

WORKDIR /reverb/rest

COPY package.json .
RUN npm install

COPY server.js .

EXPOSE $PORT