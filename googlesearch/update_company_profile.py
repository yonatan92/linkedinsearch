from time import sleep
from datetime import datetime, timedelta
import requests

GOOGLE_CUSTOM_SEARCH_ENDPOINT = "https://www.googleapis.com/customsearch/v1/siterestrict"
GOOGLE_CUSTOM_SEARCH_API_KEY = "AIzaSyCYX_7BOkE8UEYhUNxMN2ByKEPoG6qVmdQ"
GOOGLE_CUSTOM_SEARCH_CX = "47cfc6674818c71aa"



class FetchFromGoogle:
    _time_window = 100
    _reqs_per_time_window = 100
    _calls_remaining_in_window = 100
    _window_end_time = None

    @classmethod
    def _update_last_call(cls):
        if cls._window_end_time > datetime.now():
            cls._calls_remaining_in_window = cls._calls_remaining_in_window - 1
        else:
            cls._reset_window()

    @classmethod
    def _reset_window(cls):
        cls._window_end_time = datetime.now() + timedelta(seconds=cls._time_window)
        cls._calls_remaining_in_window = cls._reqs_per_time_window

    @classmethod
    def _wait_for_next_call(cls):
        if cls._window_end_time is None:
            cls._reset_window()

        _now = datetime.now()
        if cls._calls_remaining_in_window == 0:
            if cls._window_end_time > _now:
                seconds_to_wait = cls._window_end_time - _now
                sleep(seconds_to_wait.total_seconds() + 0.1)
            cls._reset_window()

    @classmethod
    def get(cls, query, retries=1):
        cls._wait_for_next_call()
        timeout_success = False
        resp = None
        while not timeout_success:
            try:
                resp = requests.get(
                    GOOGLE_CUSTOM_SEARCH_ENDPOINT,
                    params={
                        "key": GOOGLE_CUSTOM_SEARCH_API_KEY,
                        "cx": GOOGLE_CUSTOM_SEARCH_CX,
                        "q": query,
                    },
                )
            except ConnectionError:
                timeout_success = False
                sleep(2)
            else:
                timeout_success = True

        cls._update_last_call()

        # Sometimes Google returns a 500 error. if this happen we want to try again
        # twice before letting it go and raising it
        if resp and resp.status_code == 500 and retries > 0:
            return cls.get(query, retries=retries - 1)

        return resp

