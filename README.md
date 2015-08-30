# CitiBike Stats

An API to retrieve personal CitiBike user data.

### To install
1. Create a python virtual environment
2. Activate the virtual environment
3. install the dependencies

        $ virtualenv venv
        $ source venv/bin/activate
        $ pip install -r requirements.txt

### Run Server

    $ source venv/bin/activate
    (venv) $ python site/citibike_stats.py
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

### Example Use

    $ python
    >>> from utils.NYCCitiBikeParser import NYCCitiBikeParser
    >>> parser = NYCCitiBikeParser('username', 'password')
    >>> trips = parser.getTrips()
    >>> trips[0]
    {
        'start_date': 1439735157
        'end_date': 1439736653,
        'duration': 1496,
        'cost': 0.0,
        'end_station': u'Pearl St & Hanover Square',
        'start_station': u'Division St & Bowery',
    }

### Run Tests

    $ nosetests


