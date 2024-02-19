FROM python:3.8.5

COPY . /app

WORKDIR /app

RUN ["pip3", "install", "-r", "requirements.txt"]
EXPOSE 5000
CMD ["python3", "run.py"]