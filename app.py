# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

test_date = dt.datetime(2016,8,23)

stats = [
    func.min(measurement.tobs),
    func.max(measurement.tobs),
    func.avg(measurement.tobs)
]

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"This is the app<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (use YYYY-MM-DD format)<br/>"
        f"/api/v1.0/start/end (use YYYY-MM-DD format)<br/>"
    )

#Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= test_date).all()
    session.close()

    return jsonify(dict(results))

#Stations Route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.name).all()
    session.close()
    
    return jsonify(list(np.ravel(results)))

#Temperature Route
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    results = session.query(measurement.tobs).filter(measurement.station == "USC00519281").filter(measurement.date >= test_date).all()

    return jsonify(list(np.ravel(results)))

#Temperature w/ Start Date Route
@app.route("/api/v1.0/<start>")
def start(start):

    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    session = Session(engine)
    results = session.query(*stats).filter(measurement.date >= start_date).all()
    session.close()

    results_dict = {}
    results_dict["max"] = results[0][0]
    results_dict["min"] = results[0][1]
    results_dict["avg"] = results[0][2]

    return jsonify(results_dict)

#Temperature w/ Start Date and End Date Route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()
    session = Session(engine)
    results = session.query(*stats).filter(measurement.date >= start_date).filter(measurement.date <= start_date).all()
    session.close()

    results_dict = {}
    results_dict["max"] = results[0][0]
    results_dict["min"] = results[0][1]
    results_dict["avg"] = results[0][2]

    return jsonify(results_dict)

if __name__ == "__main__":
    app.run(debug = True)