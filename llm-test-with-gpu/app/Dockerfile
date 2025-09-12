FROM python:3.9-slim

RUN apt-get update && apt-get install -y git

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app.py .
COPY index.html .
EXPOSE 5000

CMD ["python3", "app.py"]
