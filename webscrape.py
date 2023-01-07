import os
import requests
import time

base_url = 'https://api.pokemontcg.io/v2/cards'

page = 1
page_size = 250
result = 0

# Set the directory to save the images
save_dir = 'pokemon_cards_data'

# Create the save directory if it doesn't already exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

while True:
    # Get the list of all cards from the API
    response = requests.get('https://api.pokemontcg.io/v2/cards', params={'page': page, 'pageSize': page_size})
    cards = response.json()['data']
    print('We are at page: #' + str(page))
    page += 1
    # Download each card image
    for card in cards:
        # Get the image URL and file name
        print('Entry #' + str(result))
        result += 1
        image_url = card['images']['large']
        image_name = card['id'].replace(' ', '_')
        image_name = image_name.replace('<', '_')
        image_name = image_name.replace('>', '_')
        image_name = image_name.replace('|', '_')
        image_name = image_name.replace('*', '_')
        image_name = image_name.replace('/', '_')
        image_name = image_name.replace('?', '_') + '.png'

        #Download the image and save it to the save directory
        response = requests.get(image_url)
        open(os.path.join(save_dir, image_name), 'wb').write(response.content)

print('Scrape complete!')