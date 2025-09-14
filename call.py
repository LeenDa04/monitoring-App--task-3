from pathlib import Path
from dotenv import load_dotenv
import os, psutil, pymysql
from datetime import datetime, timezone
import logging
from functools import wraps
logging.basicConfig(level=logging.INFO , format="%(asctime)s [%(levelname)s] %(message)s", 
                    handlers=[logging.StreamHandler(), logging.FileHandler("/var/log/collector.log")])
logger=logging.getLogger(__name__)
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)
maxSec = 86400 #which is 60*60*24 (the 24 hours in seconds)
def log_actions(func):
    @wraps(func) 
    def wrapper(*args, **kwargs):
        logging.info(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        result=func(*args, **kwargs)
        logging.info(f"Function {func.__name__} returned: {result}")
        return result
    return wrapper
@log_actions
def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
@log_actions
def ensure_schema(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS cpu_samples (ts_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, value DOUBLE NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS mem_samples (ts_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, value DOUBLE NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS disk_samples(ts_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, value DOUBLE NOT NULL)")
@log_actions
def main():
    ts=datetime.now(timezone.utc).isoformat(timespec="seconds")
    cpu=psutil.cpu_percent(interval=1)
    mem=psutil.virtual_memory().percent
    disk=psutil.disk_usage('/hostfs').percent
    with get_conn() as db:
        with db.cursor() as cur:
            ensure_schema(cur)  
            cur.execute("INSERT INTO cpu_samples  (ts_utc,value) VALUES (%s,%s)",(ts,cpu))
            logging.info(f"Collected CPU sample: {cpu}%")
            cur.execute("INSERT INTO mem_samples  (ts_utc,value) VALUES (%s,%s)",(ts,mem))
            logging.info(f"Collected mem sample: {mem}%")
            cur.execute("INSERT INTO disk_samples (ts_utc,value) VALUES (%s,%s)",(ts,disk))
            logging.info(f"Collected disk sample: {disk}%")
            cur.execute("DELETE FROM cpu_samples  WHERE ts_utc < (UTC_TIMESTAMP() - INTERVAL 24 HOUR)")
            cur.execute("DELETE FROM mem_samples  WHERE ts_utc < (UTC_TIMESTAMP() - INTERVAL 24 HOUR)")
            cur.execute("DELETE FROM disk_samples WHERE ts_utc < (UTC_TIMESTAMP() - INTERVAL 24 HOUR)")
if __name__ == "__main__": 
    main()
