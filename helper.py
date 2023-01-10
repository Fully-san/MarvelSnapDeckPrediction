import pandas as pd
import streamlit as st
from st_clickable_images import clickable_images

def addCard(deck, card):
    firstDefaultCard = deck[deck.name == 'Default']
    if not firstDefaultCard.empty:
        deck.iloc[firstDefaultCard.index[0]] = card

def createEmptyDeck(defaultCard):
    deck = pd.DataFrame(columns=defaultCard.columns)
    for i in range(12):
        deck.loc[i] = defaultCard.loc[0]
    return deck

def createSession():
    if 'cards' not in st.session_state:
        st.session_state.cards = pd.read_csv("data/cards.csv")

    if 'defaultCard' not in st.session_state:
        st.session_state.defaultCard = pd.DataFrame({
            'id' : [0],
            'name' : ['Default'],
            'art' : ['https://marvelsnapzone.com/wp-content/themes/blocksy-child/assets/media/cards/annihilus.webp?v=20'],
            'ability' : [''],
            'slug' : [''],
        })

    if 'currentDeck' not in st.session_state:
        st.session_state.currentDeck = createEmptyDeck(st.session_state.defaultCard)

    if 'decks' not in st.session_state:
        st.session_state.decks = loadDecks()

def drawCurrentDeck(deck, defaultCard, margin, cardHeight):
    clicked = clickable_images(
        list(deck['art']),
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": str(margin) + "px", "height": str(cardHeight) + "px"},
    )

    if clicked > -1 and deck.iloc[clicked]['name'] != defaultCard.iloc[0]['name']:
        deck.iloc[clicked] = defaultCard.iloc[0]
        st.experimental_rerun()

def drawDecks(topDecks, cards, cardHeigh, currentDeck = None, isDisplayAbility = False):
    for i, deck in topDecks.iterrows():
        with st.container():
            st.subheader(deck['name'])
            images = []
            titles = []
            for cardSlug in deck['slugCards'][1:-1].split(','):
                cardSlug = cardSlug.strip()
                card = cards[cards['slug'] == cardSlug].iloc[0]
                if currentDeck is not None and cardSlug in currentDeck['slug'].values:
                    images.append("https://cdn.filestackcontent.com/ANWxluLzPRk6VV28eF11Mz/monochrome/" + card['art'])
                else:
                    images.append(card['art'])
                titles.append(str(card['ability']))
                
            clicked = clickable_images(
                images,
                titles,
                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                img_style={"margin": "5px", "height": str(cardHeigh)+"px"},
            )

            if(isDisplayAbility and clicked > -1):
                cardSlug = deck['slugCards'][1:-1].split(',')[clicked]
                cardClicked = cards[cards['slug'] == cardSlug.strip()].iloc[0]
                st.header(cardClicked['name'])
                st.subheader(cardClicked['ability'])
            
            if i != len(topDecks) - 1:
                st.markdown("""---""")

def loadDecks():
    return pd.read_csv("data/decks.csv")

def resetDeck(deck, defaultCard):
    if 'deckName' in st.session_state:
        st.session_state.deckName = ""
    
    for i in range(12):
        deck.loc[i] =  defaultCard.loc[0]

def saveDeck(deck, deckName, allDeck, defaultCard):
    slugCards = []
    
    for i, card in deck.iterrows():
        slugCards.append(card['slug'])
    
    if (len(deck[deck.name == 'Default']) == 0) and (len(set(slugCards)) == len(slugCards)):
        allDeck = pd.concat([allDeck, pd.DataFrame([[deckName, slugCards, pd.to_datetime('today').strftime("%Y-%m-%d")]], columns=allDeck.columns)])
        allDeck.to_csv("data/decks.csv", index=False)
        resetDeck(deck, defaultCard)

def selectionDeck(decks, currentDeck, defaultCard, deckNumber):
    allDeckWithScore = []
    for i, deck in decks.iterrows():
        score = 0
        deckCards = [cardSlug.strip() for cardSlug in deck['slugCards'][1:-1].split(',')]
        for j, card in currentDeck.loc[currentDeck['name'] != defaultCard.iloc[0]['name']].iterrows():
            if card['slug'] in deckCards:
                score += round(100/12, 2)
                
        allDeckWithScore.append({'score' : score, 'deck' : deck})
    
    topDecksByScore = sorted(allDeckWithScore, key=lambda d: d['score'], reverse=True)[:deckNumber]
    
    topDecks = [ topDeckByScore['deck'] for topDeckByScore in topDecksByScore ]
    
    return pd.DataFrame(topDecks, columns = decks.columns)