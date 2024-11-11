FROM node:18.17.1-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN npx ngcc --properties es2023 browser module main --firts-only --create-ivy-entry-points
COPY . .
RUN npm run build
FROM nginx:stable
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist/frontend/ /usr/share/nginx/html
EXPOSE 80 



