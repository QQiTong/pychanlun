FROM node:lts-alpine as build

WORKDIR /app

COPY . .

RUN npm config set registry https://registry.npm.taobao.org/
RUN cd front && npm install && npm run build

FROM nginx:alpine

COPY --from=build /app/front/web /usr/share/nginx/html/
COPY ./front/nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
