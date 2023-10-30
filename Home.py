import re
import os
import time
import streamlit as st
from git.repo import Repo
from helper import TITLE_APPLICATION, MARVEL_ICON, DECK_CREATION_ICON, DECK_PREDICTION_ICON, HOME_ICON, checkIfUpToDate, deleteFilesInDirectory
from updateData import scrap, parseName, getCards, createCardsCSV
from st_pages import Page, show_pages

repoPath = '/Users/Fully/Documents/TCG/MarvelSnap/MarvelSnapDeckPrediction'

st.set_page_config(
    page_title=TITLE_APPLICATION,
    page_icon=MARVEL_ICON
)

show_pages(
    [
        Page("Home.py", "Home", HOME_ICON)
    ]
)

st.write('Welcome')

if 'upToDate' not in st.session_state:
    with st.spinner('Checking data updates...'):
        st.session_state['upToDate'] = checkIfUpToDate()

if not st.session_state['upToDate']:
    deleteFilesInDirectory("Data/Arts/Regular")
    deleteFilesInDirectory("Data/Arts/Fade")

    with st.status("Update Data...", expanded=True) as status: 
        getCardProgressBarText = "Retrieving cards..."
        getCardProgressBar = st.progress(0, text=getCardProgressBarText)
        cards = getCards()
        getCardProgressBar.progress(100, text=getCardProgressBarText)

        charactersProgressBarText = "Downloading card images..."
        charactersProgressBar = st.progress(0, text=charactersProgressBarText)
        charactersProgressBar.text = charactersProgressBarText
        characters = scrap(charactersProgressBar)

        createCardsProgressBarText = "Writing cards..."
        createCardsProgressBar = st.progress(0, text=createCardsProgressBarText)
        createCardsCSV(characters)
        createCardsProgressBar.progress(100, text=charactersProgressBarText)

        getCardProgressBar.empty()
        charactersProgressBar.empty()
        createCardsProgressBar.empty()

        status.update(label="Update complete!", state="complete", expanded=False)

    commitFiles = ['Data/cards.csv', 'Data/lastVersion.txt']
    for card in cards:
        name = re.sub(" the "," The ", parseName(card["name"]))
        name = re.sub("[ '\-]","", name)
        path = 'Data/Arts/Regular/' + name + '.Webp'
        if os.path.isfile(path):
            commitFiles.append(path)

        path = 'Data/Arts/Fade/' + name + '.Webp'
        if os.path.isfile(path):
            commitFiles.append(path)

    # Auto commit
    repo = Repo(repoPath)

    repo.index.add(commitFiles)
    repo.index.commit('Update new cards')

    origin = repo.remotes[0]
    origin.push()

    st.session_state['upToDate'] = True

show_pages(
    [
        # Page("Home.py", "Home", HOME_ICON),
        Page("Deck_Creation.py", "Deck Creation", DECK_CREATION_ICON),
        Page("Deck_Prediction.py", "Deck Prediction", DECK_PREDICTION_ICON)
    ]
)