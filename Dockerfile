
FROM python:3.7.3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY goss_bot ./goss_bot

CMD [ "python", "-m", "goss_bot"]
