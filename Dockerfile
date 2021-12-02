FROM python:3.9.7
EXPOSE 5000
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python3 generate.py
ENTRYPOINT ["python3", "main.py"]
