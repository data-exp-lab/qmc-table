FROM python:3.9.7-alpine3.14
EXPOSE 8000
WORKDIR /app
COPY ./index.html .
COPY ./css css
ENTRYPOINT ["python3", "-m", "http.server"]
