# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:22.16.0 AS build-stage

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application code
COPY ./ /app/

ARG VITE_SERVER_URL=${VITE_SERVER_URL}

RUN npm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
