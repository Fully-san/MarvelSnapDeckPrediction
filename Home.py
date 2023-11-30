import re
import os
import time
import streamlit as st
from git.repo import Repo
from helper import TITLE_APPLICATION, MARVEL_ICON, DECK_CREATION_ICON, DECK_PREDICTION_ICON, HOME_ICON, getUpdatedCards
from updateData import scrap, createCardsCSV
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

with st.spinner('Checking data updates...'):
    updatedCards = getUpdatedCards()

if updatedCards:
    with st.status("Update Data...", expanded=True) as status: 
        charactersProgressBarText = "Downloading card images..."
        charactersProgressBar = st.progress(0, text=charactersProgressBarText)
        charactersProgressBar.text = charactersProgressBarText
        characters = scrap(progressBar=charactersProgressBar, deleteFile=True, cardList=updatedCards)

        createCardsProgressBarText = "Writing cards..."
        createCardsProgressBar = st.progress(0, text=createCardsProgressBarText)
        createCardsCSV(characters)
        createCardsProgressBar.progress(100, text=charactersProgressBarText)

        charactersProgressBar.empty()
        createCardsProgressBar.empty()

        status.update(label="Update complete!", state="complete", expanded=False)

    commitFiles = ['Data/cards.csv', 'Data/lastVersion.txt']
    for card in updatedCards:
        path = 'Data/Arts/Regular/' + card + '.Webp'
        if os.path.isfile(path):
            commitFiles.append(path)

        path = 'Data/Arts/Fade/' + card + '.Webp'
        if os.path.isfile(path):
            commitFiles.append(path)

    # Auto commit
    repo = Repo()
    #repo = Repo('https://github.com/Fully-san/MarvelSnapDeckPrediction')

    repo.index.add(commitFiles)
    repo.index.commit('Update new cards')

    origin = repo.remotes[0]
    origin.push()

show_pages(
    [
        # Page("Home.py", "Home", HOME_ICON),
        Page("Deck_Creation.py", "Deck Creation", DECK_CREATION_ICON),
        Page("Deck_Prediction.py", "Deck Prediction", DECK_PREDICTION_ICON)
    ]
)