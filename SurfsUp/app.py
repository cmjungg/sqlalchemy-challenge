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
Base.prepare(autoload_with=engine)

# Save references to each table
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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return only the last 12 months of data of precipitation"""
    #start date for query filter
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    years_data = session.query( measurement.date, measurement.prcp).\
        filter(measurement.date > start_date).all()

    session.close()

    for date, prcp in years_data:
        converted_years_data = {date: prcp}

    return jsonify(converted_years_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of weather stations"""
    # Query all stations
    results = session.query(station.station, station.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list the dates and temperature observations of the most-active station for the previous year of data."""
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    start_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    most_active_station = 'USC00519281'

    years_data_for_station = session.query( measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date > start_date).all()

    session.close()

    # Convert list of tuples into normal list
    converted_years_data = list(np.ravel(years_data_for_station))

    return jsonify(converted_years_data)

@app.route("/api/v1.0/<start>")
def start_end(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start"""
    # Query all temperatures
    start_day = dt.datetime.strptime(start, "%m%d%Y")
    lowest_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start_day).all()
    highest_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start_day).all()
    avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start_day).all()
    
    session.close()

    # Create a dictionary 
    
    temp_dict = {}
    temp_dict["Tmax"] = highest_temp
    temp_dict["Tmin"] = lowest_temp
    temp_dict["Tavg"] = avg_temp
    

    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)
