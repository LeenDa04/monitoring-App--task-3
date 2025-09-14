from flask import Flask, jsonify
import time
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

#i did this one before doing the database so i just took the last value from the list
""""
@app.route("/cpu/current")
@log_actions
def cpu_current():
    if cpuValues:
        return jsonify({"cpu current usage percent": cpuValues[-1]})
    return jsonify({"error": "no samples yet"})
    """
@app.route("/cpu/current")
@log_actions
def cpu_current():
    with get_conn().cursor() as cur:
     cur.execute("SELECT value, ts_utc FROM cpu_samples ORDER BY ts_utc DESC LIMIT 1")
     row=cur.fetchone()
     logging.debug(f"Fetched {row} from ur database so u can get the current cpu usage")
    if row:
        value, ts_utc=row
        return jsonify({
            "cpu current usage percent": value,
            "ts_utc": ts_utc
        })
    logging.warning("no cpu samples found in database ,404 returned")

    return jsonify({"error": "no samples yet"}), 404


@app.route("/cpu/avg24h")
@log_actions
def cpu_avg24h():
    size=24 #i need 24 values , (24 hours)
    samplesPerHour =60  
    with get_conn().cursor() as cur:
      query=(f"SELECT value FROM cpu_samples ORDER BY ts_utc DESC LIMIT {size*samplesPerHour}")
      cur.execute(query)
      logging.debug(f"executing:{query}")
      rows=cur.fetchall()
      logging.debug(f"fetched:{len(rows)} rows from   ur database")
    if not rows:
      logging.warning("no cpu samples found in database ,404 returned")
      return jsonify({"error":"no samples yet"}),404
    values=[float(r[0]) for r in rows]
    forEachHour=[] #the array that will store the avg for each hourr
    i=0
    while i<len(values) and len(forEachHour)<24:
      chunk=values[i:i+samplesPerHour]
      avg=sum(chunk)/len(chunk)
      forEachHour.append(round(avg,3))
      logging.debug(f" average for hour {len(forEachHour)}:{chunk}")
      i+=samplesPerHour
    return jsonify({"cpu avg usage percent for the last 24 hours newest to oldest": forEachHour})

#memoryyyyyyyyyyyyyyyyyyyyy
@app.route("/mem/current")
@log_actions
def mem_current():
    with get_conn().cursor() as cur:
     cur.execute("SELECT value, ts_utc FROM mem_samples ORDER BY ts_utc DESC LIMIT 1")
     row=cur.fetchone()
     logging.debug(f"Fetched {row} from ur database so u can get the current mem usage")
    if row:
        value,ts_utc=row
        return jsonify({
            "mem current usage percent":value,
            "ts_utc":ts_utc
        })
    logging.warning("no mem samples found in database ,404 returned")

    return jsonify({"error": "no samples yet"}),404

@app.route("/mem/avg24h")
@log_actions
def mem_avg24h():
    size=24
    samplesPerHour=60
    with get_conn().cursor() as cur:
      query=(f"SELECT value FROM mem_samples ORDER BY ts_utc DESC LIMIT {size*samplesPerHour}")
      cur.execute(query)
      logging.debug(f"executing:{query}")
      rows=cur.fetchall()
      logging.debug(f"fetched:{len(rows)} rows from   ur mem database")
    if not rows:
      logging.warning("no mem samples found in database ,404 returned")
      return jsonify({"error": "no samples yet"}),404
    values=[float(r[0]) for r in rows]
    forEachHour=[]
    i=0
    while i<len(values) and len(forEachHour) <24:
      print("while in mem entereeeddd")
      chunk= values[i:i+samplesPerHour]
      avg=sum(chunk)/len(chunk)
      forEachHour.append(round(avg,2))
      i+=samplesPerHour
    return jsonify({"mem avg usage percent for the last 24 hours newest to oldest": forEachHour})


#diskkkkkkkkkkkkkkkkkkkkkkkkkk
@app.route("/disk/current")
@log_actions
def disk_current():
    with get_conn().cursor() as cur:
     cur.execute("SELECT value, ts_utc FROM disk_samples ORDER BY ts_utc DESC LIMIT 1")
     row=cur.fetchone()
     logging.debug(f"Fetched {row} from ur database so u can get the current disk usage")
    if row:
        value, ts_utc= row
        return jsonify({
            "disk current usage percent":value,
            "ts_utc": ts_utc
        })
    logging.warning("no disk samples found in database ,404 returned")
    return jsonify({"error": "no samples yet"}),404


@app.route("/disk/avg24h")
@log_actions
def disk_avg24h():
    size=24
    samplesPerHour=60
    with get_conn().cursor() as cur:
      query=(f"SELECT value FROM disk_samples ORDER BY ts_utc DESC LIMIT {size*samplesPerHour}")
      cur.execute(query)
      logging.debug(f"executing:{query}")
      rows=cur.fetchall()
      logging.debug(f"fetched:{len(rows)} rows from   ur database")
    if not rows:
      logging.warning("no disk samples found in database ,404 returned")
      return jsonify({"error": "no samples yet"}),404
    values= [float(r[0]) for r in rows]
    logging.debug(f"values:{values} rows from   ur disk database")
    forEachHour= []
    i =0
    while i < len(values) and len(forEachHour)< 24:
      print("while loop entered")
      chunk= values[i:i+samplesPerHour]
      if not chunk:
        break
      avg= sum(chunk)/len(chunk)
      print("avgggg is",avg)
      forEachHour.append(round(avg, 2))
      i+=samplesPerHour
      print(i)
    return jsonify({"disk avg usage percent for the last 24 hours newest to oldest": forEachHour})

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



