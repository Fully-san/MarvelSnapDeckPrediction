import os
import re
from PIL import Image
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from st_clickable_images import clickable_images

GITHUB_REPOSITORY_URL = 'https://raw.githubusercontent.com/Fully-san/MarvelSnapDeckPrediction/master/Data/Arts/'
MARVELSNAPZONE_PATCH_NOTES_URL = 'https://marvelsnapzone.com/news/patch-notes/'

TITLE_APPLICATION = "Marvel Snap Deck Prediction"
MARVEL_ICON = Image.open("Data/Icons/MarvelSnap.ico")
HOME_ICON = '⛩️'
DECK_CREATION_ICON = '🧑‍🍳' #🪛 🛠️ 🚧
DECK_PREDICTION_ICON = '🧑‍💻'#🎯

firefoxOptions = Options()
firefoxOptions.add_argument("--headless")
firefoxOptions.add_argument('--disable-dev-shm-usage')
firefoxOptions.add_argument('--disable-extensions')
firefoxOptions.add_argument('--disable-gpu')

firefoxService = Service(GeckoDriverManager().install())

def addCard(deck, card):
    firstDefaultCard = deck[deck.name == 'Default']
    if not firstDefaultCard.empty:
        deck.iloc[firstDefaultCard.index[0]] = card

def checkIfUpToDate():
    upToDate = True
    driver = webdriver.Firefox(service=firefoxService, options=firefoxOptions)
    driver.get(MARVELSNAPZONE_PATCH_NOTES_URL)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    articles = soup.findAll('article', {'class': 'entry-card'})

    articleId = articles[0]['id'].split('-')[1]

    with open('Data/lastVersion.txt', 'r+') as f:
        lastArticleID = f.read()

        upToDate = articleId == lastArticleID

        if not upToDate:
            f.seek(0)
            f.truncate()
            f.write(articleId)

    return upToDate

def createEmptyDeck():
    deck = pd.DataFrame(columns=st.session_state.defaultCard.columns)
    for i in range(12):
        deck.loc[i] = st.session_state.defaultCard.iloc[0]
    return deck

def createSession():
    if 'cards' not in st.session_state:
        st.session_state.cards = pd.read_csv("./Data/cards.csv")

    if 'defaultCard' not in st.session_state:
        st.session_state.defaultCard = pd.DataFrame({
            'name' : ['Default'],
            'art' : ['https://raw.githubusercontent.com/Fully-san/MarvelSnapDeckPrediction/master/Data/Arts/Fallback.webp'],
            'ability' : [''],
            'slug' : [''],
        })

    if 'currentDeck' not in st.session_state:
        st.session_state.currentDeck = createEmptyDeck()

    if 'decks' not in st.session_state:
        st.session_state.decks = loadDecks()
        st.session_state.decks['slugCards'] = [re.sub(r"('| )", "", s) for s in st.session_state.decks['slugCards']]

    if 'topDecksByScore' not in st.session_state:
        st.session_state.topDecksByScore = []

    # if 'deckName' not in st.session_state:
    #     st.session_state.deckName = ""

def deleteFilesInDirectory(directoryPath):
    try:
        files = os.listdir(directoryPath)
        for file in files:
            filePath = os.path.join(directoryPath, file)
            if os.path.isfile(filePath):
                os.remove(filePath)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")

def drawCurrentDeck(deck, margin, cardHeight):
    clicked = clickable_images(
        list(deck['art']),
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": str(margin) + "px", "height": str(cardHeight) + "px"},
    )

    if clicked > -1 and deck.iloc[clicked]['name'] != st.session_state.defaultCard.iloc[0]['name']:
        deck.iloc[clicked] = st.session_state.defaultCard.iloc[0]
        st.experimental_rerun()

def drawDecks(topDecks, cards, cardHeigh, currentDeck = None, isDisplayAbility = False):
    for i, deck in topDecks.iterrows():
        with st.container():
            st.subheader(deck['name'])
            images = []
            titles = []
            
            for cardSlug in deck['slugCards'][1:-1].split(','):

                cardBuffer = cards[cards['slug'] == cardSlug]

                if not cardBuffer.empty:
                    card = cardBuffer.iloc[0]
                else:
                    card = st.session_state.defaultCard.iloc[0]

                if currentDeck is not None and cardSlug in currentDeck['slug'].values:
                    images.append(GITHUB_REPOSITORY_URL + 'Fade/' + card['slug'] + '.Webp')
                else:
                    images.append(GITHUB_REPOSITORY_URL + 'Regular/' + card['slug'] +'.Webp')
                titles.append(str(card['ability']))

            clicked = clickable_images(
                images,
                titles,
                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                img_style={"margin": "5px", "height": str(cardHeigh)+"px"},
            )

            if(isDisplayAbility and clicked > -1):
                cardSlug = deck['slugCards'][1:-1].split(',')[clicked]
                cardClicked = cards[cards['slug'] == cardSlug].iloc[0]
                st.header(cardClicked['name'])
                st.subheader(cardClicked['ability'])
            
            if i != len(topDecks) - 1:
                st.markdown("""---""")

def loadDecks():
    return pd.read_csv("./Data/decks.csv")

def resetDeck():
    st.session_state.deckName = ""
    
    st.session_state.currentDeck = createEmptyDeck()

def saveDeck():
    if st.session_state.deckName == '':
        return
    
    if not st.session_state.currentDeck[st.session_state.currentDeck['name'] != 'Default']['name'].is_unique or 'Default' in st.session_state.currentDeck['name'].values:
        return

    allDeck = st.session_state.decks

    slugCards = []
    
    for i, card in st.session_state.currentDeck.iterrows():
        slugCards.append(card['slug'])
    
    if (len(set(slugCards)) == len(slugCards)):
        allDeck = pd.concat([allDeck, pd.DataFrame([[st.session_state.deckName, slugCards, 0]], columns=allDeck.columns)])

    allDeck.to_csv("./Data/decks.csv", index=False)
    resetDeck()

def selectionDeck(decks, currentDeck, deckNumber):
    allDeckWithScore = []
    for i, deck in decks.iterrows():
        score = 0
        deckCards = [cardSlug for cardSlug in deck['slugCards'][1:-1].split(',')]
        for j, card in currentDeck.loc[currentDeck['name'] != st.session_state.defaultCard.iloc[0]['name']].iterrows():
            if card['slug'] in deckCards:
                score += round(100/12, 2)
                
        allDeckWithScore.append({'score' : score, 'deck' : deck})
    
    st.session_state.topDecksByScore = sorted(allDeckWithScore, key=lambda d: d['score'], reverse=True)[:deckNumber]
    
    topDecks = [topDeckByScore['deck'] for topDeckByScore in st.session_state.topDecksByScore]
    
    return pd.DataFrame(topDecks, columns = decks.columns)

def validDeck():
    bestScore = max([topDeck['score'] for topDeck in st.session_state.topDecksByScore])
    allValidDeckNames = [topDeck['deck']['name']  for topDeck in st.session_state.topDecksByScore if topDeck['score'] == bestScore]

    decks = loadDecks()

    for deckName in allValidDeckNames:
        decks.loc[decks['name'] == deckName, 'score'] += 1

    decks = decks.sort_values(by=['score'], ascending=False)
    
    decks.to_csv("./Data/decks.csv", index=False)
    resetDeck()