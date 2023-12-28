import os
import pandas as pd
import streamlit as st
from src.aux import get_folder_from_path
from streamlit_extras.switch_page_button import switch_page
st.set_page_config(page_title="Moby")
st.title('Model Builder')

option = st.radio('',['Start with the data I have',
                      'Just curious'])
click = st.button('Go')

if click:
    if option == 'Just curious':
        file_read = pd.read_csv('example_data/Multivariate_Linear_Regression.csv')
        column_names = list(file_read.columns.values)
        st.session_state.update({'col_names': column_names,
                                 'raw_data': file_read,
                                 'path': get_folder_from_path(os.path.abspath(__file__))[0]})
    switch_page('data_prep')