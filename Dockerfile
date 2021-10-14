FROM python:3.9.7
EXPOSE 5000
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./main.py .
COPY ./main.js .
COPY ./body.html .
COPY ./css css
ENTRYPOINT ["python3", "main.py"]
