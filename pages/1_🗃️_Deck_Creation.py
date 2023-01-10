import streamlit as st
from helper import createSession, addCard, saveDeck, resetDeck, drawCurrentDeck, drawDecks

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title="MarvelSnap Deck Creation",
    page_icon="🗃️",
)

createSession()

with st.container():
    st.text_input('Deck name', key="deckName")
    
    with st.container():
        drawCurrentDeck(st.session_state.currentDeck, st.session_state.defaultCard, 5, 130)
        
    selectedCard = st.selectbox('', list(st.session_state.cards['name']))
    
    c1, c2, c3, c4 = st.columns([1, 1, 1, 12])
        
    with c1:
        st.button('Add card', on_click=addCard, args=(st.session_state.currentDeck, st.session_state.cards.loc[st.session_state.cards['name'] == selectedCard].values, ))
            
    with c2:
        st.button('Save deck', on_click=saveDeck, args=(st.session_state.currentDeck, st.session_state.deckName, st.session_state.cards, st.session_state.defaultCard, ))

    with c3:
        st.button('Reset deck', on_click=resetDeck, args=(st.session_state.currentDeck, st.session_state.defaultCard, ))
    
st.markdown("""---""")

with st.container():
    drawDecks(st.session_state.decks, st.session_state.cards, 130)