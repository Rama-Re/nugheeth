import os
import requests


def get_directions(origin, destination, language='ar', mode='driving'):
    api_key = 'AIzaSyDkPh8vuUbdAuQCSf971rWxQ_uTxvi2pqc'

    url = (
        'https://maps.googleapis.com/maps/api/directions/json'
        f'?origin={origin}&destination={destination}'
        f'&key={api_key}&overview=full&mode={mode}&language={language}'
    )

    response = requests.get(url)
    response.raise_for_status()
    return response.json()