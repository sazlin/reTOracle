from SECRETS import SECRETS
from datumbox import DatumBox



datum_box = DatumBox(SECRETS['datumbox_api'])
datum_box.twitter_sentiment_analysis("I love my cat")