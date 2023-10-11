import streamlit as st
from helper import TITLE_APPLICATION, MARVEL_ICON, createSession, addCard, saveDeck, resetDeck, drawCurrentDeck, drawDecks
from st_pages import Page, hide_pages

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title=TITLE_APPLICATION,
    page_icon=MARVEL_ICON,
)

hide_pages(["Deck Creation"])

createSession()

with st.container():
    st.text_input(label='Deck name', key='deckName')
    # st.session_state.deckName = st.text_input('Deck name')

    st.session_state.deckNameRequiredMessage = st.empty()
    
    with st.container():
        drawCurrentDeck(st.session_state.currentDeck, 5, 130)
        st.session_state.missingCardsMessage = st.empty()
        
    selectedCard = st.selectbox('', list(st.session_state.cards['name']))
    
    c1, c2, c3, c4 = st.columns([1, 1, 1, 12])
        
    with c1:
        st.button('Add card', on_click=addCard, args=(st.session_state.currentDeck, st.session_state.cards.loc[st.session_state.cards['name'] == selectedCard].values))
            
    with c2:
        if st.button('Save deck', on_click=saveDeck):
            isValid = True
            st.session_state.deckNameRequiredMessage.empty()
            st.session_state.missingCardsMessage.empty()

            if st.session_state.deckName == '':
                st.session_state.deckNameRequiredMessage.error("Deck name is a required field.")
                isValid = False

            if not st.session_state.currentDeck[st.session_state.currentDeck['name'] != 'Default']['name'].is_unique and 'Default' in st.session_state.currentDeck['name'].values:
                st.session_state.missingCardsMessage.error("Twelve cards are needed to create a deck and you can't have the same card more than once.")
                isValid = False
            elif not st.session_state.currentDeck[st.session_state.currentDeck['name'] != 'Default']['name'].is_unique:
                st.session_state.missingCardsMessage.error("You can't have the same card more than once.")
                isValid = False
            elif 'Default' in st.session_state.currentDeck['name'].values:
                st.session_state.missingCardsMessage.error("Twelve cards are needed to create a deck.")
                isValid = False

    with c3:
        st.button('Reset deck', on_click=resetDeck)
    
st.markdown("""---""")

with st.container():
    drawDecks(st.session_state.decks, st.session_state.cards, 130)