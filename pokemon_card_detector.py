import cv2
import os
import pandas as pd
import numpy as np
import imagehash
import urllib
import requests
import keyboard
from PIL import Image
from pokemontcgsdk import Card

# Replace YOUR_API_KEY with your actual API key
api_key = "eeee1e2c-40e0-4daf-8440-f3a00fb3a332"

save_dir = 'detected_cards'

def distance(str1, str2):
    i = 0
    count = 0
 
    while(i < len(str1)):
        if(str1[i] != str2[i]):
            count += 1
        i += 1
    return count


# Capture video from the webcam
video_capture = cv2.VideoCapture(0)

# Load in dataset
df = pd.read_csv('pokemon_cards.csv')

imageURL = 'https://www.pngkit.com/png/full/241-2417192_blank-pokemon-card-template-best-photos-of-pokemon.png'
cardName = 'Unknown'
price = 'N/A'

#Download the image from the URL
response = urllib.request.urlopen(imageURL)

#Read the image data and convert it to a NumPy array
image_data = response.read()
frame2 = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_UNCHANGED)



while True:
    # Get the current frame from the webcam
    ret, frame = video_capture.read()

    # Get the width and height of the image
    height, width, _ = frame.shape

    cv2.putText(frame, 'Place your card here:', (150, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Calculate the coordinates of the top-left and bottom-right corners of the rectangle
    x1 = width // 2 - 95
    y1 = height // 2 - 130
    x2 = width // 2 + 95
    y2 = height // 2 + 130

    # Draw a rectangle in the middle of the image
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if cv2.waitKey(1) == 32:

        subImage = frame[y1:y2, x1:x2]
        card = Image.fromarray(subImage)
        cardPhash = str(imagehash.phash(card))
        # Calculate the distance between the given value and each value in the "phash" column
        df['distance'] = df['phash'].apply(distance, args=(cardPhash,))

        # Find the row with the minimum distance
        min_row = df['distance'].idxmin()

        # Obtain the filename
        cardID = (df.loc[min_row, 'filename']).split('.')[0]
    

        response = requests.get(f"https://api.pokemontcg.io/v2/cards/{cardID}", headers={"Authorization": api_key})

        # Check for a successful request
        if response.status_code == 200:
            # Get the card data from the response
            card_data = response.json()["data"]

            # Print the name and image URL of the card
            cardName = card_data['name']
            imageURL = card_data['images']['large']
            try:
                price = card_data['cardmarket']['prices']['averageSellPrice']
            except:
                price = 'No price found'

            print(cardName)
            print(imageURL)
        
            mycard = requests.get(imageURL)
            frame2 = cv2.imdecode(np.frombuffer(mycard.content, np.uint8), cv2.IMREAD_UNCHANGED)
            frame2 = cv2.resize(frame2, (0,0), fx=0.6, fy=0.6)
            open(os.path.join(save_dir, cardName+ '.png'), 'wb').write(mycard.content)

        else:
            print("An error occurred while fetching the card data.")

    cv2.putText(frame, f'Card identifed is {cardName}' , (120, 415), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f'The average price is ${price}' , (110, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Pokemon Card Detection App', frame)
    # Display the image
    cv2.imshow("Your Pokemon Card", frame2)
    # Show the frame


    # Break the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
# Release the video capture and destroy all windows
video_capture.release()
cv2.destroyAllWindows()



