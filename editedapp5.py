from flask import Flask, jsonify
import logging
import pymysql
from functools import wraps
import os
from pathlib import Path
from datetime import datetime , timezone
from dotenv import load_dotenv

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG , format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(), logging.FileHandler("/var/log/monitor.log")])
logger=logging.getLogger(__name__)
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=True)
maxSec = 86400 #which is 60*60*24 (the 24 hours in seconds)

def get_conn():

    try:
        return pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            autocommit=True
        )
    except Exception as e:
        logging.fatal(f"Database connection failed: {e}")

def log_actions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        result=func(*args, **kwargs)
        logging.info(f"Function {func.__name__} returned: {result}")
        return result
    return wrapper

#i created this global function so i can just call it with the suitable parameter
def get_current(table: str):
    if not table:
        return jsonify({"error": "unknown table"}), 400
    with get_conn().cursor() as cur:
     cur.execute(f"SELECT value, ts_utc FROM {table} ORDER BY ts_utc DESC LIMIT 1")
     row=cur.fetchone()
     logging.debug(f"Fetched {row} from {table} so you can get the current {table} usage")
    if row:
        value, ts_utc = row
        return jsonify({
            f"{table} current usage percent": value,
            "ts_utc": ts_utc
        })
    logging.warning(f"no {table} samples found in database ,404 returned")
    return jsonify({"error": "no samples yet"}),404


def get_avg24h(table:str):
    size=24
    samplesPerHour=60
    if not table:
        return jsonify({"error": "unknown table"}), 400
    with get_conn().cursor() as cur:
      query = f"SELECT value FROM {table} ORDER BY ts_utc DESC LIMIT {size*samplesPerHour}"
      cur.execute(query)
      logging.debug(f"executing:{query}")
      rows = cur.fetchall()
      logging.debug(f"fetched:{len(rows)} rows from  ur {table} database")
    if not rows:
      logging.warning(f"no {table} samples found in database ,404 returned")
      return jsonify({"error":"no samples yet"}),404
    values=[float(r[0]) for r in rows]
    forEachHour = []  # the array that will store the avg for each hour
    i=0
    while i<len(values) and len(forEachHour) < size:
      chunk=values[i:i+samplesPerHour]
      avg=sum(chunk) /len(chunk)
      forEachHour.append(round(avg,3))
      logging.debug(f" average for hour {len(forEachHour)}:{chunk}")
      i+=samplesPerHour
    return jsonify({f"{table} avg usage percent for the last {size} hours newest to oldest": forEachHour})


class base:
    def __init__(self, table:str):
        self.table = table      

    def current_json(self):
        return get_current(self.table)

    def avg24h_json(self):
        return get_avg24h(self.table)
    

class Cpu(base):
    def __init__(self):
        super().__init__("cpu_samples")

class Mem(base):
    def __init__(self):
        super().__init__("mem_samples")

class Disk(base):
    def __init__(self):
        super().__init__("disk_samples")


#cpuuuuuuuuuuuuuuuuuuuuuuuuuuuu
@app.route("/cpu/current")
@log_actions
def cpu_current():
    return Cpu().current_json()


@app.route("/cpu/avg24h")
@log_actions
def cpu_avg24h():
    return Cpu().avg24h_json()


#memoryyyyyyyyyyyyyyyyyyyyy
@app.route("/mem/current")
@log_actions
def mem_current():
    return Mem().current_json()

@app.route("/mem/avg24h")
@log_actions
def mem_avg24h():
   return Mem().avg24h_json()

#diskkkkkkkkkkkkkkkkkkkkkkkkkk
@app.route("/disk/current")
@log_actions
def disk_current():
    return Disk().current_json()


@app.route("/disk/avg24h")
@log_actions
def disk_avg24h():
    return Disk().avg24h_json()

@app.route("/")
@log_actions
def index():
     return (
        "<body style=\"background-image: url('/static/background.jpg'); "
        "background-size: cover; background-position: center; background-repeat: no-repeat;\">"

        "<div style='background-color: rgba(0,0,0,0.5); color: white; padding: 20px;'>"
        "<h1>Task 3</h1>"
        "<h2> Welcome :)) </h2>"
        "<h3>Server Monitor</h3>"
        "<ul>"
        "<li><a href='/cpu/current' style='color: #00ffcc;'>cpu current usage</a></li>"
        "<li><a href='/cpu/avg24h' style='color: #00ffcc;'>cpu avg usage for the last 24 hours</a></li>"
        "<li><a href='/mem/current' style='color: #00ffcc;'>memory current usage</a></li>"
        "<li><a href='/mem/avg24h' style='color: #00ffcc;'>memory avg usage for the last 24 hours</a></li>"
        "<li><a href='/disk/current' style='color: #00ffcc;'>disk current usage</a></li>"
        "<li><a href='/disk/avg24h' style='color: #00ffcc;'>disk avg usage for the last 24 hours</a></li>"
        "</ul>"
        "</div>"
        "</body>"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True , use_reloader=False)


