import os
import streamlit as st
from src.aux import make_path, get_folder_from_path

st.set_page_config(page_title="Moby - Data prep")
st.title('Data prep')

file = st.file_uploader('Choose file')

if file:
    path = get_folder_from_path(os.path.abspath(__file__))
    value = 'my_project'
    st.write("Create Folder:")
    out_path = st.text_input('please enter folder name or leave empty for default',
                             value=make_path(path,value))
    click = st.button("Go")
    if click:
        os.makedirs(name=out_path)