FROM node:20.6.0 AS build-stage

ADD package.json /package.json

ENV NODE_PATH=/node_modules
ENV PATH=$PATH:/node_modules/.bin
RUN npm install -g npm
RUN npm install

WORKDIR /app
ADD . /app
COPY dist /app/dist
# RUN npm run build

FROM nginx:1.25.1 AS prodction-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
RUN apt-get update &&  apt-get install -y wget
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
