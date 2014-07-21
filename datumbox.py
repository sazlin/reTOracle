from urllib2 import Request, urlopen
from urllib import urlencode
import json


class DatumBox():

    base_url = "http://api.datumbox.com/1.0/"

    def __init__(self, api_key):
        self.api_key = api_key

    def sentiment_analysis(self, text):
        """Possible responses are "positive", "negative" or "neutral" """
        return self._classification_request(text, "SentimentAnalysis")

    def twitter_sentiment_analysis(self, text):
        """Possible responses are "positive", "negative" or "neutral" """
        return self._classification_request(text, "TwitterSentimentAnalysis")

    def is_spam(self, text):
        """Returns a boolean"""
        response = self._classification_request(text, "SpamDetection")
        return response == "spam"

    def is_adult_content(self, text):
        """Returns a boolean"""
        response = self._classification_request(text, "AdultContentDetection")
        return response == "adult"

    def detect_language(self, text):
        """Returns an ISO_639-1 language code"""
        return self._classification_request(text, "LanguageDetection")

    def is_commercial(self, text):
        """Returns "commercial" or "noncommercial" """
        response = self._classification_request(text, "CommercialDetection")
        return response == "commercial"

    def is_educational(self, text):
        """Returns boolean"""
        response = self._classification_request(text, "EducationalDetection")
        return response == "educational"

    def _classification_request(self, text, api_name):
        full_url = DatumBox.base_url + api_name + ".json"
        return self._send_request(full_url, {'text' : text})

    def _send_request(self, full_url, params_dict):
        params_dict['api_key'] = self.api_key
        request = Request(url=full_url, data=urlencode(params_dict))
        f = urlopen(request)
        response = json.loads(f.read())


        if "error" in response['output']:
            raise DatumBoxError(response['output']['error']['ErrorCode'], response['output']['error']['ErrorMessage'])
        else:
            return response['output']['result']


class DatumBoxError(Exception):
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message



    def __str__(self):
        return "Datumbox API returned an error: " + str(self.error_code) + " " + self.error_message