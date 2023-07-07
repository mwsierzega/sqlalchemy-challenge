# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>Precipitation Analysis<br/>"
        f"/api/v1.0/precipitation<br/><br/>All Stations<br/>"
        f"/api/v1.0/stations<br/><br/>Dates and Temperature of Most Active Stations<br/>"
        f"/api/v1.0/tobs<br/><br/>Minimum, Maximum, and Average Temperature<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data for the last 12 months"""
    # Query the last 12 months of data
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    one_year = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    results = session.query(measurement.date, func.avg(measurement.prcp)).filter(measurement.date >= one_year).group_by(measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipication_last12
    precipication_last12 = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipication_last12.append(precipitation_dict)

    return jsonify(precipication_last12)

@app.route("/api/v1.0/stations")
def all_stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data for the last 12 months"""
    # Query all stations
    results = session.query(station.id, station.station, station.name, station.latitude, station.longitude, station.elevation).all()

    session.close()

    # Create a dictionary of all_stations
    all_station = []
    for id, station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["Id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_station.append(station_dict)
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query
    results = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    session.close()

    # Create dictionary
    temperature = []
    for station, count in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["count"] = count
        temperature.append(tobs_dict)
    return jsonify(temperature)

@app.route("/api/v1.0/<start>")
def calculated_temps(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    # Create dictionary
    temp_minavgmax = {}
    temp_minavgmax["min_temp"] = results[0][0]
    temp_minavgmax["avg_temp"] = results[0][1]
    temp_minavgmax["max_temp"] = results[0][2]
    return jsonify(temp_minavgmax)

@app.route("/api/v1.0/<start>/<end>")
def calculated_temps_last(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    # Create dictionary
    temp_minavgmax_last = {}
    temp_minavgmax_last["min_temp"] = results[0][0]
    temp_minavgmax_last["avg_temp"] = results[0][1]
    temp_minavgmax_last["max_temp"] = results[0][2]
    return jsonify(temp_minavgmax_last)

if __name__ == '__main__':
    app.run(debug=True)
