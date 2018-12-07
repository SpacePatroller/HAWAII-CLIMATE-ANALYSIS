import numpy as np

import pandas as pd
import datetime as dt
from datetime import datetime

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
        f"Precip:-----------------/api/v1.0/precipitation</br>"
        f"Station List:----------/api/v1.0/stations</br>"
        f"12 Month Temps:---/api/v1.0/tobs</br>"
        f"Min Max Avg From:--/api/v1.0/yyyy dd mm"
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


#   `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.



#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.



#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<date>")
def start_date(date):

    date = datetime.strptime(date, '%Y%m%d')
    date_ = date.date()
    
    min_max_avg_temp = session.query((Measurement.date),func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= date_).group_by(Measurement.date).all()
    
    data = list(np.ravel(min_max_avg_temp))
    
    return jsonify(data)

    
    #push all three to a dictionary and then return the dictionary?





if __name__ == "__main__":
    app.run(debug=True)