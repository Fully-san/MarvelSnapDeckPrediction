import streamlit as st
from helper import TITLE_APPLICATION, MARVEL_ICON, createSession, addCard, validDeck, resetDeck, drawCurrentDeck, drawDecks, selectionDeck
from st_pages import Page, hide_pages

st.set_page_config(
    layout="wide",
    page_title=TITLE_APPLICATION,
    page_icon=MARVEL_ICON,
)

hide_pages(["Deck Prediction"])

from st_pages import Page, show_pages

createSession()

with st.sidebar:
    selectedCard = st.selectbox('card', list(st.session_state.cards['name']), label_visibility='hidden')
    
    with st.container():
        st.button('Add card', on_click=addCard, args=(st.session_state.currentDeck, st.session_state.cards.loc[st.session_state.cards['name'] == selectedCard].values))
        
    with st.container():
        drawCurrentDeck(st.session_state.currentDeck, 0, 130)

    with st.container():
        c1, c2, c3 = st.columns([0.4,0.2,0.4])
        with c1:
            st.button(':green[Valid deck]', on_click=validDeck)

        with c3:
            st.button(':red[Reset deck]', on_click=resetDeck)


drawDecks(selectionDeck(st.session_state.decks, st.session_state.currentDeck, 10), st.session_state.cards, 200, st.session_state.currentDeck, True)