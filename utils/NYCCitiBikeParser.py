import mechanize
import cookielib
from bs4 import BeautifulSoup
###
from .NYCCitiBikeParserExceptions import NYCCitiBikeLoginError


class NYCCitiBikeParser:

    ###
    ### Constants
    ###

    login_url = 'https://member.citibikenyc.com/profile/login'
    login_form_action = 'https://member.citibikenyc.com/profile/login_check'
    login_success_url = 'https://member.citibikenyc.com/profile/'
    trips_page_url = 'https://member.citibikenyc.com/profile/trips/{partner_user_id}?pageNumber={page_index}'

    ###
    ### Public
    ###

    def __init__(self, username, password):
        self.__initialize_browser()
        self.__login(username, password)

    def getTrips(self):
        """
        Returns an array of the logged in users trips
        """
        # Retrieve and parse the trips page
        trips_page_html = self.__get_trips_page_html()
        trips_page = BeautifulSoup(trips_page_html, 'html.parser')

        # Check the 'last' button to see how many pages of results there are
        final_page_index = int(trips_page.find('a', class_='ed-paginated-navigation__pages-group__link_last').attrs['href'].split('pageNumber=')[1])

        parsed_trips = []

        for page_index in range(final_page_index+1):
            trips_page_html = self.__get_trips_page_html(page_index)
            trips_page = BeautifulSoup(trips_page_html, 'html.parser')

            trips = trips_page.find('div', class_='ed-table__items')
            
            for trip in trips:
                # TODO : This is strange, but while adding a test, sometimes trip was a 
                # <class 'bs4.element.NavigableString'> instead of e <class 'bs4.element.Tag'>
                if type(trip) != type(trips):
                    continue
                parsed_trip = {}
                parsed_trip['start_date'] = trip.find('div', class_='ed-table__item__info__sub-info_trip-start-date').text.strip()
                parsed_trip['start_station'] = trip.find('div', class_='ed-table__item__info__sub-info_trip-start-station').text.strip()
                parsed_trip['end_date'] = trip.find('div', class_='ed-table__item__info__sub-info_trip-end-date').text.strip()
                parsed_trip['end_station'] = trip.find('div', class_='ed-table__item__info__sub-info_trip-end-station').text.strip()
                parsed_trip['duration'] = trip.find('div', class_='ed-table__item__info_trip-duration').text.strip()
                parsed_trip['cost'] = trip.find('div', class_='ed-table__item__info_trip-cost').text.strip()

                parsed_trips.append(parsed_trip)

        return parsed_trips

    ###
    ### Private
    ###

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

        self._partner_user_id = profile_page.find('a', class_="ed-panel__link_last-trip").attrs['href'].split('/profile/trips/')[1].split('?')[0]

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