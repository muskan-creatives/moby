import streamlit as st
from streamlit_extras.switch_page_button import switch_page
st.set_page_config(page_title="Moby")
st.title('Model Builder')

option = st.radio('',['Start with the data I have',
                      'Just curious'])
click = st.button('Go')

if click:
    if option == 'Start with the data I have':
        switch_page('data_prep')
    else:
        pass
