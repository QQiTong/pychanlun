FROM python:3.7.4

WORKDIR /opt/app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "-m", "back.server"]