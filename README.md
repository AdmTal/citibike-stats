# CitiBike Stats

An API to retrieve personal CitiBike user data.

### To install
1. Create a python virtual enviroment
2. Activate the virtual enviroment
3. install the dependancies

        $ virtualenv venv
        $ source venv/bin/activate
        $ pip install -r requirements.txt

### Example Use

    python
    >>> from utils.NYCCitiBikeParser import NYCCitiBikeParser
    >>> parser = NYCCitiBikeParser('username', 'password')
    >>> trips = parser.getTrips()
    >>> trips[0]
    {
        'end_date': u'08/22/20158: 52: 47AM',
        'end_station': u'Pearl St & Hanover Square',
        'duration': u'9min 17s',
        'cost': u'$0.00',
        'start_station': u'Division St & Bowery',
        'start_date': u'08/22/2015 8:43:30AM'
    }

### Run Tests

    $ nosetests


