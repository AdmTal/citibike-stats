import unittest
from mock import MagicMock, patch
from mechanize import Browser
from bs4 import BeautifulSoup
###
from utils.NYCCitiBikeParser import NYCCitiBikeParser

### Test data
trips_page_0 = open('tests/sample_data/trips_page_0.html').read()
trips_page_1 = open('tests/sample_data/trips_page_1.html').read()


class NYCCitiBikeParserTest(unittest.TestCase):

    @patch.object(NYCCitiBikeParser, '_NYCCitiBikeParser__login')
    @patch.object(NYCCitiBikeParser, '_NYCCitiBikeParser__initialize_browser')
    @patch.object(NYCCitiBikeParser, '_NYCCitiBikeParser__get_trips_page_html', 
        side_effect=[trips_page_0, trips_page_0, trips_page_1])
    def test_getTrips(self, mock_login, mock_initialize_browser, mock_get_trips_page_html):

        parser = NYCCitiBikeParser('username', 'password')
        trips = parser.getTrips()

        # check that there are 20 trips
        trip_count = len(trips)
        self.assertEquals(trip_count, 20, "There should be 20 trips, but there are {}".format(trip_count))

        # check that each trip has all of the fields
        for trip in trips:
            self.assertIn('start_date', trip, "Each trip should have an 'start_date'")
            self.assertIn('start_station', trip, "Each trip should have an 'start_station'")
            self.assertIn('end_date', trip, "Each trip should have an 'end_date'")
            self.assertIn('end_station', trip, "Each trip should have an 'end_station'")
            self.assertIn('duration', trip, "Each trip should have an 'duration'")
            self.assertIn('cost', trip, "Each trip should have an 'cost'")

        # check that the 5th trip matches the expected format
        # from my lovely trip to Governers Island
        governers_island_trip = {
            'end_date': '08/16/2015 10:50:53 AM',
            'end_station': 'Soissons Landing',
            'duration': '24 min 56 s',
            'cost': '$0.00',
            'start_station': 'Soissons Landing',
            'start_date': '08/16/2015 10:25:57 AM'
        }

        self.assertEquals(trips[4], governers_island_trip)




