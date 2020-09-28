#
# import json
# import csv
# from enum import IntFlag
from urllib.parse import urlparse
# import tldextract
# import numpy as np
# from googlesearch.update_company_profile import FetchFromGoogle
#
# url = "https://everthere.co"
# url_parse = urlparse(url)
# host_name = url_parse.netloc
# query_param_one = "Website: "
# query_param_two = "Company size: "
# query_param_third = "Headquarters: "

#
# class Result:
#     """
#      class that represents single result from google restrict search
#     """
#
#     def __init__(self, link, snippet):
#         """
#         :param link: the link of linkedin that rhe result get from.
#         :param snippet: the snippet of the result.
#         """
#         self.link = link
#         self.snippet = snippet.replace('\n', '')
#         self.result_data = {"link_is_www": False, "has_website_match": False, "has_size": False, "has_headquarters": False}
#         self.website, self.size, self.headquarter = self.parse_data_result(self)
#         self.state = self.calc_result_state()
#
#     def __repr__(self):
#         return f'<Result {self.link, self.snippet}>'
#
#     def calc_result_state(self):
#         """
#         each result have a state that represents what the result have from what the query asked for.
#         :return: the state of current result
#         """
#
#         # boolean list of result data -
#         # values_list[0]- link is of the form of "www..."
#         # values_list[1]- found website match in result snippet."
#         # values_list[2]- found company size in snippet."
#         # values_list[3]- found headquarters in result snippet."
#         values_list = list(self.result_data.values())
#         # the index of True value in values_list
#         bit_wise_list = np.array(values_list, dtype=bool)*1
#         state_number = self.bits_list_to_int(bit_wise_list)
#
#         return self.State(int(state_number))
#
#     @staticmethod
#     def parse_data_result(self):
#         website_index, company_size_index, headquarters_index = self.find_index_of_query()
#         website_result = self.extract_data_from_snippet(website_index, 1)
#         size_result = self.extract_data_from_snippet(company_size_index, 2)
#         headquarters_result = self.extract_data_from_snippet(headquarters_index, 3)
#         self.check_website_match(website_result)
#         self.link_is_www()
#
#         return website_result, size_result, headquarters_result
#
#     def link_is_www(self):
#         if urlparse(self.link).netloc.startswith('www'):
#             self.result_data["link_is_www"] = True
#
#     def extract_data_from_snippet(self, index, query_number):
#         substring_result = None
#         if index != -1:
#             switcher_extract_data = {
#                  1: self.extract_data_substring(index, len(query_param_one), query_number),
#                  2: self.extract_data_substring(index, len(query_param_two), query_number),
#                  3: self.extract_data_substring(index, len(query_param_third), query_number),
#                  }
#
#             substring_result = switcher_extract_data.get(query_number, None)
#
#             if query_number == 2:
#                 self.result_data["has_size"] = True
#             elif query_number == 3:
#                 self.result_data["has_headquarters"] = True
#
#         return substring_result
#
#     def extract_data_substring(self, index, length, query_number):
#         switcher = {
#             1: self.snippet[index+length:].split(' ')[0][:-1],
#             2: self.snippet[index+length:].split(' ')[0],
#             3: self.snippet[index+length:].split('.')[0],
#         }
#
#         return switcher.get(query_number, None)
#
#     def extract_headquarters_substring(self, index, length):
#         substring = self.snippet[index + length:].split('.')[0]
#
#         return substring
#
#     def check_website_match(self, website_result):
#         if len(urlparse(website_result).netloc) != 0:
#             if tldextract.extract(host_name).suffix == tldextract.extract(urlparse(website_result).netloc).suffix:
#                 if tldextract.extract(host_name).domain == tldextract.extract(urlparse(website_result).netloc).domain:
#                     self.result_data["has_website_match"] = True
#
#     def bits_list_to_int(self, list):
#         res = 0
#         for ele in list:
#             res = (res << 1) | ele
#
#         return res
#
#     def find_index_of_query(self):
#         """
#         :return: the indexes of the queries params in the snippet.
#         """
#         website_index = self.snippet.find(query_param_one)
#         company_size_index = self.snippet.find(query_param_two)
#         headquarters_index = self.snippet.find(query_param_third)
#
#         return website_index, company_size_index, headquarters_index
#
#     class State(IntFlag):
#         """
#         state options for each result, each result can have few things - the result link is of the form www, found
#         website match in snippet, found size company from snippet, found headquarters from snippet.
#         L- Has Link of the form www
#         W - Has website match in snippet
#         S - Has size company in snippet
#         H - Has headquarters in snippet
#         """
#
#         L = 8,
#         W = 4,
#         S = 2,
#         H = 1,
#         Nothig = 0,
#
#
#
# def fetch_data_from_google():
#
#     print(FetchFromGoogle.get(f'{url} "{query_param_one} OR {query_param_two} OR {query_param_third}"').json())

# fetch_data_from_google()

# def add_results_to_list(data_items):
#     list_items = []
#     for item in data_items["items"]:
#         list_items.append(Result(item["link"], item["snippet"]))
#
#     return list_items
#
#
#
#
#
# def extract_company_data_from_linkedin():
#     # data = fetch_data_from_google()
#     with open('example.json') as f:
#         results_list = []
#         data = json.load(f)
#         for result in data["items"]:
#             results_list.append(Result(result["link"], result["snippet"]))
#     for item in results_list:
#         print(item.link)
#         print(item.website)
#         print(item.size)
#         print(item.headquarter)
#         print(item.state)
#         print("----------------------------")
#
#     with open("info.csv", 'w', newline='') as new_file:
#         csv_writer = csv.writer(new_file)
#         csv_writer.writerow(['Website', 'Size', 'Headquarters'])
#         found = True
#         for result in results_list:
#             if result.state == result.State(15):
#                 csv_writer.writerow([result.website, result.size, result.headquarter])
#                 found = False
#                 break
#         if found:
#             for result in results_list:
#                 if result.state == result.State(7):
#                     csv_writer.writerow([result.website, result.size, result.headquarter])
#                     break
#
# # results_list = add_results_to_list(data)
# #
#
#
# (results_list)
#
#
# # if __name__ ==  __main__:
# extract_company_data_from_linkedin()
#
#
#
#
#
#
