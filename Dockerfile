FROM node:18.16.1

ADD package.json /package.json

ENV NODE_PATH=/node_modules
ENV PATH=$PATH:/node_modules/.bin
RUN npm install -g npm
RUN npm install

WORKDIR /app
ADD . /app
RUN npm run build

FROM nginx:1.25.1 AS prodction-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
