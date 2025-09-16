import requests

class Scryfall:
    BASE_URL = "https://api.scryfall.com"

    header = {}
    @staticmethod
    def get_random_card():
        response = requests.get(f"{Scryfall.BASE_URL}/cards/random", headers=Scryfall.header)
        if response.status_code == 200:
            return response.json()
        else:
            return "Not found"
        
    @staticmethod
    def search_card(card):
        if card['number'] and card['set']:
            print(f"Searching for card with set: {card['set']} and number: {card['number']}")
            response = requests.get(f"{Scryfall.BASE_URL}/cards/{card['set']}/{card['number']}", headers=Scryfall.header)
            # print(f"{response.json()}")
            if response.status_code == 200:
                return response.json()
        print(f"Searching for card with name: {card['name']}")
        response = requests.get(f"{Scryfall.BASE_URL}/cards/named", params={"fuzzy": card['name']}, headers=Scryfall.header)
        # print(f"{response.json()}")
        if response.status_code == 200:
            return response.json()
        else:
            return "Not found"