FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends cron util-linux
WORKDIR /app
COPY req.txt /app/
RUN pip install --no-cache-dir -r req.txt
COPY editedapp4.py call.py /app/

COPY collector.cron /etc/cron.d/collector
RUN chmod 0644 /etc/cron.d/collector

COPY static/ /app/static/
COPY start.sh /app/
RUN chmod +x /app/start.sh

ENV DB_HOST="" \
    DB_PORT="3306" \
    DB_NAME="" \
    DB_USER="" \
    DB_PASSWORD=""

EXPOSE 5000

CMD ["/app/start.sh"]

