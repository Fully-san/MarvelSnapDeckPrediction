import streamlit as st
from helper import createSession, addCard, resetDeck, drawCurrentDeck, drawDecks, selectionDeck

st.set_page_config(
    layout="wide",
    page_title="MarvelSnap Deck Prediction",
    page_icon="🎯",
)

createSession()

with st.sidebar:
    selectedCard = st.selectbox('card', list(st.session_state.cards['name']), label_visibility='hidden')
    
    with st.container():
        c1, c2 = st.columns([2,1])

        with c1:
            st.button('Add card', on_click=addCard, args=(st.session_state.currentDeck, st.session_state.cards.loc[st.session_state.cards['name'] == selectedCard].values, ))

        with c2:
            st.button('Reset deck', on_click=resetDeck, args=(st.session_state.currentDeck, st.session_state.defaultCard, ))
        
    with st.container():
        drawCurrentDeck(st.session_state.currentDeck, st.session_state.defaultCard, 0, 130)
        
drawDecks(selectionDeck(st.session_state.decks, st.session_state.currentDeck, st.session_state.defaultCard, 10), st.session_state.cards, 200, st.session_state.currentDeck, True)