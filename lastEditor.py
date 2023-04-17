import requests
import json
import pandas as pd
API_KEY = 'e2630c64338004c988612946d2a12a44'
USER_AGENT = 'RobFarrington'

def lastfm_get(payload):
    # define headers and URL
    headers = {'user-agent': USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'

    # Add API key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = 'json'

    response = requests.get(url, headers=headers, params=payload)
    return response

r = lastfm_get({
    'method': 'library.getArtists',
    'user':'robfarrington'
})
#print(r.json())
df=pd.DataFrame(r.json()['artists']['artist'])
print(r.status_code)
print(df.head())