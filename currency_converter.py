"""
CURRENCY CONVERTOR

CLI based currency convertor
The program connects with an API to provide real-time exchange rates
The details for the API connection are stored in a configuration file

Command Format:

    >> currency_converter.py <from_currency_code> <to_currency_code> <amount>

        currency code : International Currency Code (3 letters)
        amount        : OPTIONAL. Default value is 1.0

To Print All Available Currency codes:

    >> currency_coverter -codes|--codes


===========================================================
GUI Implementation : currency_converter_gui.py

API Used : https://rapidapi.com/fyhao/api/currency-exchange

Developer : Raman Chawla
"""


import configparser
import json
import requests

from dotenv import load_dotenv
from sys import argv
from os import getenv


FILE_PATH = "./Files/"

API_DATA = {"CONFIG_FILE": FILE_PATH + "cc_config.INI",
            "NAME": 'CurrencyExchangeAPI',
            "URL_HEADER": "URL",
            "URL_HEADER_CURRENCIES": "URL_Quotes"}

CURRENCY_JSON_FILE = FILE_PATH + "currencies.json"


load_dotenv("./Files/.env")  # Loading environment variables


class CurrencyConverterException(Exception):
    """Exception class for Currency Converter"""

    def __init__(self, *args):
        super().__init__(*args)


class APIConnection:
    """
    Class containing API Connection data
    """

    def __init__(self, api_dict):
        self.__api = api_dict["NAME"]
        self.__config_file = api_dict["CONFIG_FILE"]
        self.__url_header = api_dict["URL_HEADER"]
        self.__url_header_currencies = api_dict["URL_HEADER_CURRENCIES"]

        self.config = self.__get_api_config()
        self.__access_headers = tuple(name.strip()
                                      for name in self.config['Headers'].split(','))

    def __get_api_config(self):
        """Reads configuration file & Returns API configuration"""
        config = configparser.ConfigParser()
        config.read(self.__config_file)
        try:
            return config[self.__api]
        except KeyError as ke:
            raise CurrencyConverterException(
                "API Configuration file / data is missing!") from ke

    def get_api_access_headers(self):
        """Returns API Headers dictionary required to communicate with API"""
        try:
            headers = {header: getenv(header)  # Fetching value from environment
                       for header in self.__access_headers}
        except KeyError as ke:
            raise CurrencyConverterException("Invalid API Headers") from ke
        else:
            return headers

    def get_url(self):
        """Returns URL for connecting to server for currency conversion"""
        return self.config[self.__url_header]

    def get_url_currencies(self):
        """Returns URL for fetching available currency codes from the server"""
        return self.config[self.__url_header_currencies]


class CurrencyConverter:
    """
    Class to implement currency converter
    """

    def __init__(self, api_connection=APIConnection(API_DATA)):
        """Class Constructor : Ensures all connections and configurations"""
        self.__all_currencies = CurrencyConverter.__get_all_currencies()

        self.__api_headers = api_connection.get_api_access_headers()
        self.__api_url = api_connection.get_url()
        self.__api_url_currencies = api_connection.get_url_currencies()

        self.__available_currencies = tuple(self.__fetch_currencies_from_api())

    def __check_values(self, code_source, code_target, amount):
        """Checks currency codes and amount for validity, Raises Error otherwise"""
        if not self.is_valid_currency_code(code_source):
            raise CurrencyConverterException("Invalid Currency Code : "
                                             + code_source)
        elif not self.is_currency_code_available(code_source):
            raise CurrencyConverterException("Sorry '" + code_source
                                             + "' is not currently supported.")

        if not self.is_valid_currency_code(code_target):
            raise CurrencyConverterException("Invalid Currency Code : "
                                             + code_target)
        elif not self.is_currency_code_available(code_target):
            raise CurrencyConverterException("Sorry '" + code_target
                                             + "' is not currently supported.")

        if not CurrencyConverter.is_valid_amount(amount):
            raise CurrencyConverterException("Invalid Amount : " + amount)

    def __fetch_currencies_from_api(self):
        """Fetches Currency Codes available with the API and Returns List"""
        try:
            response = requests.get(self.__api_url_currencies,
                                    headers=self.__api_headers, timeout=5)
        except requests.exceptions.RequestException as re:
            raise CurrencyConverterException("SERVER NOT REACHABLE : "
                                             + str(re)) from re
        else:
            if response.status_code == 200:
                return sorted(json.loads(response.text))
            else:
                raise CurrencyConverterException("Server Response Code -",
                                                 response.status_code)

    @staticmethod
    def __get_all_currencies():
        """Reads currency codes and names from JSON file and Returns as a dictionary"""
        try:
            with open(CURRENCY_JSON_FILE) as json_file:
                currencies = json.load(json_file)
        except FileNotFoundError as fe:
            raise CurrencyConverterException(str(fe)) from fe
        else:
            return currencies

    def convert(self, code_source, code_target, amount="1.0"):
        """
        Returns the converted amount from one currency code to other
        Returns None if both currency, codes are same"""
        if code_source != code_target:
            self.__check_values(code_source, code_target, amount)

            data = {"to": code_target, "from": code_source, "q": "1.0"}

            try:

                response = requests.get(self.__api_url, params=data,
                                        headers=self.__api_headers, timeout=5)
            except requests.exceptions.RequestException as re:
                raise CurrencyConverterException("SERVER NOT REACHABLE : "
                                                 + str(re)) from re
            else:
                if response.status_code == 200:
                    return float(amount)*float(response.text)
                else:
                    raise CurrencyConverterException("Server Response Code -",
                                                     response.status_code)
        else:
            return None

    def get_api_headers(self):
        """Returns the headers used for connecting to the API"""
        return self.__api_headers

    def get_api_url(self):
        """Returns the API URL used for connecting to the server"""
        return self.__api_url

    def get_api_url_currencies(self):
        """Returns the URL used for fetching available currency codes from API"""
        return self.__api_url_currencies

    def get_available_currencies(self):
        """Returns a dictionary of available currency codes and their full names"""
        currency_dict = {}
        for code in self.__available_currencies:
            currency_dict[code] = self.get_currency_name(code)
        return currency_dict

    def get_currency_name(self, code):
        """Returns the full currency name for the currency code passed as argument"""
        return self.__all_currencies[code]

    @staticmethod
    def is_valid_amount(amount):
        """Returns True if amount is a number, False otherwise"""
        try:
            float(amount)
        except ValueError:
            return False
        else:
            return True

    def is_valid_currency_code(self, code):
        """Returns True for a valid currency code, False otherwise"""
        return code in self.__all_currencies

    def is_currency_code_available(self, code):
        """Returns True if the currency code is available with the API, False otherwise"""
        return code in self.__available_currencies

    def print_all_currency_codes(self):
        """Prints currency codes and names of currencies"""
        for code, name in sorted(self.__all_currencies.items(), key=lambda x: x[0]):
            print(code, name, sep=" : ")

    def print_available_currencies(self):
        """Prints currency codes and names of currencies available with the API"""
        for code, name in sorted(self.__all_currencies.items(), key=lambda x: x[0]):
            print(code, name, sep=" : ")


# ----- SCRIPT -----
if __name__ == "__main__":
    api_conn = APIConnection(API_DATA)

    cc = CurrencyConverter(api_conn)

    if len(argv) in (3, 4) and len(argv[1]) == 3 and len(argv[2]) == 3:
        code_source, code_target = argv[1], argv[2]
        amount = 1.0 if len(argv) == 3 else argv[3]

        try:
            result = cc.convert(code_source, code_target, amount)
        except CurrencyConverterException as cce:
            print(str(cce))
        else:
            if result is None:
                print("Same Currency Codes Used : Conversion not required.")
            else:
                amount = float(amount)
                print(result)

                print(amount, end=" ")
                print(
                    f"{code_source} ({cc.get_currency_name(code_source)})", end=" = ")
                print(result, end=" ")
                print(f"{code_target} ({cc.get_currency_name(code_target)})")

    elif len(argv) == 2 and argv[1] in ("-codes, --codes"):
        print("\n", "Available Currency Codes are :", "\n")
        for code, name in cc.get_available_currencies().items():
            print(code, name, sep=" : ")
    else:
        print("\n Invalid Arguments!")
        print(__doc__)
