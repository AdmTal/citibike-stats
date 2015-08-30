import time
import datetime
import mechanize
import cookielib
from bs4 import BeautifulSoup
###
from .NYCCitiBikeParserExceptions import NYCCitiBikeLoginError


class NYCCitiBikeParser:
    ###
    ### Constants
    ###

    # urls
    login_url = 'https://member.citibikenyc.com/profile/login'
    login_form_action = 'https://member.citibikenyc.com/profile/login_check'
    login_success_url = 'https://member.citibikenyc.com/profile/'
    trips_page_url = 'https://member.citibikenyc.com/profile/trips/{partner_user_id}?pageNumber={page_index}'

    # classes
    start_date_class = 'ed-table__item__info__sub-info_trip-start-date'
    start_station_class = 'ed-table__item__info__sub-info_trip-start-station'
    end_date_class = 'ed-table__item__info__sub-info_trip-end-date'
    end_station_class = 'ed-table__item__info__sub-info_trip-end-station'
    duration_class = 'ed-table__item__info_trip-duration'
    cost_class = 'ed-table__item__info_trip-cost'

    last_link_class = 'ed-paginated-navigation__pages-group__link_last'
    last_trip_class = 'ed-panel__link_last-trip'

    # Citibike Date Format
    # 08/22/2015 8:52:47AM
    date_format = "%m/%d/%Y %I:%M:%S %p"

    ###
    ### Public
    ###

    def get_trips(self):
        """
        Returns an array of the logged in users trips
        """
        # Retrieve and parse the trips page
        trips_page_html = self.__get_trips_page_html()
        trips_page = BeautifulSoup(trips_page_html, 'html.parser')

        # Check the 'last' button to see how many pages of results there are
        final_page_index = int(
            trips_page.find('a', class_=self.last_link_class).attrs['href'].split('pageNumber=')[1])

        parsed_trips = []

        for page_index in range(final_page_index + 1):
            trips_page_html = self.__get_trips_page_html(page_index)
            trips_page = BeautifulSoup(trips_page_html, 'html.parser')

            trips = trips_page.find('div', class_='ed-table__items')

            for trip in trips:
                # TODO : This is strange, but while adding a test, sometimes trip was a 
                # <class 'bs4.element.NavigableString'> instead of a <class 'bs4.element.Tag'>
                # trips is the correct type, so currently checking against its type every time
                if type(trip) != type(trips):
                    continue

                parsed_trip = dict()

                # Parse Start Date
                parsed_trip['start_date'] = self.__parse_date(
                    trip.find('div', class_=self.start_date_class).text.strip()
                )

                # Parse End Date
                parsed_trip['end_date'] = self.__parse_date(
                    trip.find('div', class_=self.end_date_class).text.strip()
                )

                parsed_trip['start_station'] = trip.find('div', class_=self.start_station_class).text.strip()
                parsed_trip['end_station'] = trip.find('div', class_=self.end_station_class).text.strip()

                # Parse Duration
                parsed_trip['duration'] = self.__parse_duration(
                    trip.find('div', class_=self.duration_class).text.strip()
                )

                # Parse Cost
                parsed_trip['cost'] = self.__parse_cost(
                    trip.find('div', class_=self.cost_class).text.strip()
                )

                parsed_trips.append(parsed_trip)

        return parsed_trips

    ###
    ### Private
    ###

    def __init__(self, username, password):
        self.__initialize_browser()
        self.__login(username, password)

    def __parse_date(self, date):
        """
        Accepts a date, and returns a UNIX timestamp
        """
        if date and date != '-':
            return int(time.mktime(datetime.datetime.strptime(date, self.date_format).timetuple()))
        else:
            return 0

    def __parse_duration(self, duration):
        """
        Accepts a duration, an returns the duration in seconds
        """
        if duration and duration != '-':
            minutes, seconds = duration.split(' min ')
            minutes = int(minutes)
            if seconds:
                seconds = int(seconds.rstrip('s'))
            else:
                seconds = 0

            return (minutes * 60) + seconds

        else:
            return 0

    def __parse_cost(self, cost):
        """
        Accepts a cost string, and returns a float
        """
        if cost:
            return float(cost[1:])
        else:
            return float(0)

    def __get_trips_page_html(self, page_index=0):
        """
        Accepts a page index, and returns a page from a users trip history
        """
        return self._browser.open(self.trips_page_url.format(
            partner_user_id=self._partner_user_id,
            page_index=page_index)).read()

    def __login(self, username, password):
        """
        Attempts to log in a NYC CitiBike with using username and password
        Throws NYCCitiBikeLoginError on failure
        """
        self._browser.open(self.login_url)
        self._browser.select_form(predicate=lambda f: f.attrs.get('action', None) == self.login_form_action)
        self._browser.form['_username'] = username
        self._browser.form['_password'] = password
        self._browser.submit()

        if self._browser.geturl() != self.login_success_url:
            raise NYCCitiBikeLoginError("Login unsuccessful")

        # parse partner_user_id
        profile_page_html = self._browser.response().read()
        profile_page = BeautifulSoup(profile_page_html, 'html.parser')

        self._partner_user_id = \
            profile_page.find('a', class_=self.last_trip_class).attrs['href'].split('/profile/trips/')[1].split('?')[0]

    def __initialize_browser(self):
        """
        Prepares the internal mechanize browser option for scraping
        """
        browser = mechanize.Browser()

        cookie_jar = cookielib.LWPCookieJar()
        browser.set_cookiejar(cookie_jar)

        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        browser.addheaders = [('User-agent', 'Chrome')]

        self._browser = browser