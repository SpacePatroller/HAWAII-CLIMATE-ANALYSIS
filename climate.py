import numpy as np

import pandas as pd
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask , jsonify


engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    
    return(
        f"Lets hope this information sticks!</br>"
        f"/api/v1.0/precipitation</br>"
        f"Station List: /api/v1.0/stations</br>"
        f"12 Month Temps: /api/v1.0/tobs"
    )

# Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def prcp():

    # All info from Measurment Table
    results = session.query(Measurement.date,Measurement.prcp).all()

    weather_data = []
    for weather in results:
        weather_dict = {}    
        weather_dict[weather.date] = weather.prcp
        weather_data.append(weather_dict)

    return jsonify(weather_data)


# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def station():

    stations = session.query(Station.station).all()
    return jsonify(stations)

# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():

    #find last data point
    #last_date = session.query(func.max(Measurement.date)).all()
    conn = engine.connect()
    measurements = pd.read_sql("Select * From Measurement" ,conn)
    measurements['date'] = pd.to_datetime(measurements['date'])
    twelve_months_ago = measurements['date'].max() - pd.DateOffset(months=12)
    date_twelve = twelve_months_ago.date()

    max_station_12 = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date > date_twelve).all()

    return jsonify(max_station_12)

if __name__ == "__main__":
    app.run(debug=True)