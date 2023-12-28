# miscellaneous functions

import os
import platform
import streamlit as st
from st_aggrid import JsCode

system = platform.system()
if system == 'Windows':
    delimiter = "\\"
else:
    delimiter = "/"


def make_path(file_path,file):
    split_path = file_path.split(delimiter)
    return delimiter.join(split_path) + delimiter + file


def get_folder_from_path(file_path):
    split_path = file_path.split(delimiter)
    path, filename = split_path[:-1], split_path[-1]
    return delimiter.join(path), filename


@st.cache_resource
@st.cache_data
def include_first_col(list_of_columns:list, include_first_col:bool):
    if include_first_col:
        return list_of_columns
    else:
        return list_of_columns[1:]


valuebox_renderer = JsCode("""
class DataReader{

    init(params) {
        this.params = params;

        this.eGui = document.createElement('input');
        this.eGui.type = 'valuebox';
        this.eGui.valued = params.value;

        this.valuedHandler = this.valuedHandler.bind(this);
        this.eGui.addEventListener('click', this.valuedHandler);
    }

    valuedHandler(e) {
        let valued = e.target.valued;
        let colId = this.params.column.colId;
        this.params.node.setDataValue(colId, valued);
    }

    getGui(params) {
        return this.eGui;
    }

    destroy(params) {
    this.eGui.removeEventListener('click', this.valuedHandler);
    }
}//end class
""")
