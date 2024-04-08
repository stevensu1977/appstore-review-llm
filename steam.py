import requests
from bs4 import BeautifulSoup

def get_steam_app_id(game_name):
    response = requests.get(url=f'https://store.steampowered.com/search/?term={game_name}&category1=998', headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    app_id = soup.find(class_='search_result_row')['data-ds-appid']
    return app_id

def get_steam_reviews(appid, params={'json':1}):
    url = 'https://store.steampowered.com/appreviews/'
    response = requests.get(url=url+appid, params=params, headers={'User-Agent': 'Mozilla/5.0'})
    return response.json()

def get_steam_n_reviews(appid, n=100,review_type:str="all"):
    reviews = []
    cursor = '*'
    params = {
        'json': 1,
        'filter': 'all',
        'language': 'english',
        'day_range': 9223372036854775807,
        'review_type': review_type, # 'all', 'positive', 'negative'
        'purchase_type': 'all'
    }

    while n > 0:
        params['cursor'] = cursor.encode()
        params['num_per_page'] = min(100, n)
        n -= 100

        response = get_steam_reviews(appid, params)
        cursor = response['cursor']
        reviews += response['reviews']

        if len(response['reviews']) < 100:
            break

    return reviews




# app_id = get_steam_app_id('Counter-Strike: Global Offensive')
# print(app_id)

# reviews = get_steam_n_reviews(app_id, n=3)
# print(reviews)