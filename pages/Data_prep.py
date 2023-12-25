import os

import pandas as pd
import streamlit as st
from src.input_output import read_any
from src.aux import make_path, get_folder_from_path

st.set_page_config(page_title="Moby - Data prep")
st.title('Data prep')

file = st.file_uploader('Choose file')

if file:
    file_read = read_any(file)
    path,_ = get_folder_from_path(os.path.abspath(__file__))
    value = 'my_project'
    out_path = st.text_input('Create a working folder :',
                             value=make_path(path,value))
    click = st.button("Go")
    if click:
        os.makedirs(name=out_path)