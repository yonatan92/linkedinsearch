
# import json
# import csv
import enum
from enum import IntFlag
from urllib.parse import urlparse
import tldextract
# import numpy as np
from googlesearch.update_company_profile import FetchFromGoogle

# url = "www.microsoft.com"
# url_parse = urlparse("https://" + url)
# host_name = url_parse.netloc
query_params_pattern_dict = {
                 "website": "Website: ",
                 "size": "Company size: ",
                 "headquarters": "Headquarters: "
                 }


class Result:
    """
     Class that represents single result from google restrict search
    """

    def __init__(self, link, snippet, query_params_dict, enum_state, url):
        """
        :param link: the link of linkedin that rhe result get from.
        :param snippet: the snippet of the result.
        """
        self.url = url
        self.host_name = urlparse("https://" + self.url).netloc
        self.query_params_pattern_dict = query_params_dict
        self.link = link
        self.snippet = snippet.replace('\n', '')
        self.params_index = self.find_params_index_in_snippet()
        self.params_data_from_snippet = self.extract_data_of_query_from_snippet()
        self.result_data = self.exists_data_in_snippet()
        self.enum_state = enum_state
        self.state = self.calc_result_state()

    def __repr__(self):
        return f'<Result {self.link, self.snippet}>'

    def calc_result_state(self):
        """
        each result have a state that represents what the result have from what the query asked for.
        the state set from the bool values of result data. the method convert the result data dict to list of binary
        values and then calculate this binary array to int (example: [1,0,0,0]->8) and set the corresponding state for
        the integer.
        :return: the state of current result
        """
        # bool list of values from result data
        values_list = list(self.result_data.values())
        # the index of True value in values_list
        bit_wise_list = list(map(lambda x: 1 if x else 0, values_list))
        # convert bits list too integer for example [1,0,0,0] -> 8
        state_number = int("".join(str(x) for x in bit_wise_list), 2)

        return self.enum_state(state_number)

    def link_is_www(self):
        """
        Checks if the sub-domain of the linkedin url Is of the form of "www"
        :return: boolean- if sub-domain is "www"
        """
        result = False
        if urlparse(self.link).netloc.startswith('www'):
            result = True

        return result

    def extract_data_substring(self, key, value, index):
        """
        this method extract the data of the query params in google snippet by their pattern.
        :param key: the query param which will extract data for.
        :param value: the pattern in the google snippet of the query param which will extract data for.
        :param index: index position of the pattern in google snippet.
        :return: sub-string of data from result snippet.
        """
        if key == "website":
            result = self.snippet[index+len(value):].split(' ')[0]
        else:
            result = self.snippet[index+len(value):].split('.')[0]

        return result

    def has_website_match(self):
        """
        Checks if the website that found in snippet are matched to the website in the query by
        comparison of the URL parts.
        :return:
        """
        result = False
        website_result = self.params_data_from_snippet['website']
        if len(urlparse(website_result).netloc) != 0:
            if tldextract.extract(self.host_name).suffix == tldextract.extract(urlparse(website_result).netloc).suffix:
                if tldextract.extract(self.host_name).domain == tldextract.extract(urlparse(website_result).netloc).domain:
                    result = True

        return result

    def exists_data_in_snippet(self):
        """
        This method checks if the query params are exists and matched to the requirements.
        :return: dict that represent exist status of the requirements
        """
        result = {"link_is_www": self.link_is_www()}
        for key, value in self.params_data_from_snippet.items():
            if value is None:
                result[key] = False
            elif key == 'website':
                result[key] = self.has_website_match()
            else:
                result[key] = True

        return result

    def find_params_index_in_snippet(self):
        """
        Search the pattern position of query param in result snippet.
        example: return {"website": 15}
        :return: index of query params pattern in result snippet.
        """
        result = {}
        # for each query param search position in snippet.
        for key in self.query_params_pattern_dict:
            result[key] = self.snippet.find(self.query_params_pattern_dict.get(key))

        return result

    def extract_data_of_query_from_snippet(self):
        """
        :return: dict of params keys and values of substring that extract from result snippet.
        """
        result = {}
        for key, value in self.query_params_pattern_dict.items():
            index = self.params_index.get(key)
            # if param pattern found in snippet
            if index != -1:
                result[key] = self.extract_data_substring(key, value, index)
            else:
                result[key] = None

        return result

    def update_state(self):
        """
        re-calculate the result data and result state.
        """
        self.result_data = self.exists_data_in_snippet()
        self.state = self.calc_result_state()


def add_results_to_list(data_items, query_params_dict, url):
    """
     append results search to list
    :param data_items: the data we get from google search request
    :param query_params_dict: the query params we search data for in results
    :param url: the url of the company we search data for.
    :return: list of results from search.
    """
    # create enum dynamically depends the parameters we search data.
    enum_state = create_dynamic_enum(query_params_dict)
    list_items = []
    for item in data_items["items"]:
        list_items.append(Result(item["link"], item["snippet"], query_params_dict, enum_state, url))

    return list_items


def fetch_data_from_google(request):
    """
    make the request to google search API.
    :param request: string of request
    :return: the json result from google response
    """
    result = FetchFromGoogle.get(request).json()
    print(result)

    return result


def parse_request_from_query_params(params, url):
    """
    create a string request from the query params
    :param params: the parameters we seek data from
    :param url: the url of the company we search data for.
    :return: string for google request
    """
    request = f'{url} ' + (' OR '.join(params.keys()))

    return request


def find_best_result_data(result_list, query_params, url, first_try):
    """
    write to csv file data and return if data wrote to csv file.
    :param result_list: the list with result from request google search
    :param query_params: the params asked from google search.
    :param first_try: boolean that represent if the script search for the best result in the first time or not.
    :param url: the url of the company we search data for.
    :return:if data wrote to csv file.
    """
    res = None
    not_find_result = True
    for result in result_list:
        # case the result have all required info
        if result.state == result.enum_state(pow(2, len(result.result_data)))-1:
            res = tuple(result.params_data_from_snippet.values())
            not_find_result = False
            break
    if not_find_result:
        for result in result_list:
            # Case the result have all info but link is not "www"
            if result.state == result.enum_state(pow(2, len(result.result_data)-1))-1:
                res = tuple(result.params_data_from_snippet.values())
                break
    # case we didn't find good result so we approach google search again
    elif first_try and not_find_result:
            res = re_request_from_google(result_list, query_params, url)
    # print(res)
    return res


def create_dynamic_enum(query_params_dict):
    """
    Create Enum in dynamic way depending the amount and the kind of the query params. for different params will
    be different Enum. the Enum represent the result state. Example : for query param "website" the enum will be:
    "LINK_IS_WWW" = 4
    "WEBSITE" = 2
    "NOTHING" = 0

    the enum values is represent by 2^(the index of the param-1)
    :param query_params_dict: dict with the params that required.
    :return:
    """
    # dict that will convert to enum
    enum_dict = {}
    index = len(query_params_dict) + 1
    # set the first key,value in dict
    enum_dict["LINK_IS_WWW"] = pow(2, index - 1)
    index -= 1
    # insert all key params to dict and calculate their value.
    for key in query_params_dict:
        enum_dict[key.upper()] = pow(2, index - 1)
        index -= 1
    # set the first key,value in dict
    enum_dict["NOTHING"] = 0
    # convert dict to enum
    dynamic_enum = enum.Enum('State', enum_dict, type=IntFlag)

    return dynamic_enum


def extract_company_data_from_linkedin(query_params_dict, url):
    """
     parse request for google search API, analyze the data and write to csv file the relevant data.
    :param query_params_dict: the query parameters for the google API request
    :param url: the url of the company we search data for.
    """
    request = parse_request_from_query_params(query_params_dict, url)
    data = fetch_data_from_google(request)
    results_list = add_results_to_list(data, query_params_dict, url)
    best_result_data = find_best_result_data(results_list, query_params_dict,url, True)

    return best_result_data


def search_for_not_found_query_data(dict_data_prev_result_list, query_params):
    """
    Extract which data of query params not found in results and add those params to list with out duplicates.
    :param dict_data_prev_result_list: dictionary with link of result as key and result from google as value.
    :param query_params: the query params pattern dict from first google search API.
    :return: list of all combinations of params that data not found in first google search API.
    """
    result = []
    # for all result that we get from first google search API query.
    # example: for result with data {"website": None , "size": "11-20 employees"}, {"website": "Website: "} will add
    # to result
    for values in dict_data_prev_result_list.values():
        new_query_params = {}
        # for all the data in result we add dictionary to list with the params with value of None(not get them in query)
        for key, val in values.params_data_from_snippet.items():
            if val is None:
                new_query_params[key] = query_params[key]
        # block duplicates
        if len(new_query_params) > 0 and new_query_params not in result:
            result.append(new_query_params)

    return result


def request_per_params_are_none(new_params_dict_list, dict_data_prev_result_list, url):
    """
    request with the params that are none(did not find data params in first request) and update the new info
    that find with the associated result links in first request.
    :param new_params_dict_list:dict with links as key and dict of params data that not found as values.
    :param dict_data_prev_result_list:dict with links as key and result as value.
    :param url: the url of the company we search data for.
    :return:
    """
    # for each pattern of params we found as None, we search and request with those params in google search API
    for params in new_params_dict_list:
        request = parse_request_from_query_params(params, url)
        data = fetch_data_from_google(request)
        new_results_list = add_results_to_list(data, params, url)
        # for all new results that we get, we check which result link are also in previous result link
        # and then update the data we get in previous result
        for result in new_results_list:
            for key, value in result.params_data_from_snippet.items():
                # check if result link are also in previous results
                if result.link in dict_data_prev_result_list:
                    # update the new data we get in corresponding previous result
                    dict_data_prev_result_list[result.link].params_data_from_snippet[key] = value
                    # recalculate result properties and state after update data
                    dict_data_prev_result_list[result.link].update_state()


def re_request_from_google(prev_result_list, query_params, url):
    """
     Made new request to google search API if the last request did not yield all Required data follow the query params.
    :param prev_result_list: list of results from the first request from google search API
    :param query_params: the query params from the first request from google search API.
    :param url: the url of the company we search data for.
    """
    # write_new_request_to_csv(dict_data_prev_result_list, prev_result_list)
    dict_data_prev_result_list = {}
    # create dict from the results we get - > {result.link: result}
    for result in prev_result_list:
        dict_data_prev_result_list[result.link] = result
    # all the data not found for each result from google search API query.
    new_params_dict_list = search_for_not_found_query_data(dict_data_prev_result_list, query_params)
    # request again from google search API with the parameters that not found data
    request_per_params_are_none(new_params_dict_list, dict_data_prev_result_list, url)
    # find the best result again after we update the results with new data
    result = find_best_result_data(list(dict_data_prev_result_list.values()), query_params, False)

    return result


def companies_linkedin_data(url_list, params_pattern_dict):

    result = map(lambda x: extract_company_data_from_linkedin(params_pattern_dict, x), url_list)

    return list(result)
# extract_company_data_from_linkedin(query_params_pattern_dict, url)


companies_linkedin_data(["www.microsoft.com", "www.everthere.co", "www.intezer.com", "www.jenkins.io"],query_params_pattern_dict)















