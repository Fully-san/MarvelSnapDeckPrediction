import re
import requests
import os
import pandas as pd
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from threading import Thread
from datetime import datetime
from selenium import webdriver

from helper import driver

MARVELSNAPZONE_URL = 'https://marvelsnapzone.com/cards'
MARVELSNAPZONE_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=cards&searchcardstype=true'

def getCards():
    print("[%s] %s" % (datetime.now(), "Starting retrieving cards ..."))
    response = requests.get(MARVELSNAPZONE_API_URL)

    if response.status_code == 200:
        json_data = response.json()
        success = json_data.get("success", {})
        return success.get("cards", [])
    else:
        print(f"Error: Request failed with status code {response.status_code}")

def scrap(progressBar = None):
    print("[%s] %s" % (datetime.now(), "Starting scraping ..."))

    driver.get(MARVELSNAPZONE_URL)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    links = soup.findAll('a', {'class': 'simple-card'})

    characters = []
    for link in links:
        character = {
            'name': link['data-name'].title(),
            'ability': capitalize(BeautifulSoup(link['data-ability'], 'html.parser').text),
            'url': link['data-src'].split('?')[0],
            'status': link['data-status']
        }
        characters.append(character)
        print("[%s] %s" % (datetime.now(), f"Found {character['name']}"))

    imageUrls = [character['url'] for character in characters]
    downloadImages(imageUrls, progressBar=progressBar)

    return characters

def capitalize(text):
    punctuationFilter = re.compile('([.!?;:]\s*)')
    splitWithPunctuation = punctuationFilter.split(text)
    for i, j in enumerate(splitWithPunctuation):
        if len(j) > 1:
            splitWithPunctuation[i] = j[0].upper() + j[1:]
    text = ''.join(splitWithPunctuation)
    return text

def downloadImages(urls, dirName='Data/Arts', progressBar = None):
    regularDirName = dirName + '/Regular'
    if not os.path.exists(regularDirName):
        os.mkdir(regularDirName)
        print("[%s] %s" % (datetime.now(), f"Directory '{regularDirName}' created."))
    else:
        print("[%s] %s" % (datetime.now(), f"Directory '{regularDirName}' already exists."))

    threads = []
    for i, url in enumerate(urls):
        threads.append(Thread(target=downloadImage, args=(url, dirName)))
        threads[-1].start()

        if progressBar != None:
                progressBar.progress((i+1) / len(urls), text=progressBar.text)
    for thread in threads:
        thread.join()

    print("[%s] %s" % (datetime.now(), f"Finished downloading. Check '{regularDirName}' directory."))

def downloadImage(url, dirName):
    print("[%s] %s" % (datetime.now(), f"Download image from {url}"))
    try:
        response = requests.get(url)
        response.raise_for_status()
        fileName = re.sub("[ '\-]","", url.rsplit('/', 1)[-1].rsplit('?', 1)[0].title())
        filePath = os.path.join(dirName + '/Regular', fileName)
        with open(filePath, 'wb') as file:
            file.write(response.content)

            img = Image.open(BytesIO(response.content))
            datas = img.getdata()

            newData = []
            for item in datas:
                if item[3] != 0:
                    newData.append((item[0], item[1], item[2], 50))
                else:
                    newData.append((item[0], item[1], item[2], item[3]))
            else:
                newData.append(item)

            newData = newData[:-1]
            img.putdata(newData)
            img.save(dirName + '/Fade/' + fileName)

    except requests.exceptions.RequestException as e:
        print("[%s] %s" % (datetime.now(), f"Error downloading image from URL '{url}': {e}"))

def parseName(name):
    name = name.strip()

    name_mappings = {
        "Ant Man": "Ant-Man",
        "Jane Foster Mighty Thor": "Jane Foster The Mighty Thor",
        "Super-Skrull": "Super Skrull",
    }

    return name_mappings.get(name, name)

def parseAbility(ability):
    ability = ability.strip()

    if not ability:
        ability = "No ability"

    return ability

def createCardsCSV(cards, dirName='Data'):
    cards_df = pd.DataFrame({'name': pd.Series(dtype='str'), 'art': pd.Series(dtype='str'), 'ability': pd.Series(dtype='str'), 'slug': pd.Series(dtype='str')})

    for card in cards:
        # Silk is noted as unreleased
        if card["status"] != "released" and card["name"] != "Silk":
            continue

        name = parseName(card["name"])
        art = card["url"],
        ability = parseAbility(card["ability"])
        slug = slug.replace(" the ", " The ")
        slug = re.sub("[ \-]","", name)
        if "'" in slug:
            index = slug.index("'")
            slug = slug[:index]  + slug[index+1].upper() + slug[index+2:]
            slug = re.sub("[']","", slug)
        
        cards_df = pd.concat([cards_df, pd.DataFrame([[name, art[0], ability, slug]], columns=cards_df.columns)])
    
    cards_df.to_csv(dirName + "/cards.csv", index=False)