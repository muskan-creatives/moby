import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from src.input_output import read_any
from src.aux import get_folder_from_path, delimiter, valuebox_renderer
from st_aggrid import AgGrid, GridOptionsBuilder


@st.cache_data
def save_csv(file:pd.DataFrame, path, filename, deli=delimiter):
    file.to_csv(path + deli + filename)


@st.cache_data
def plot(dataframe, dependent, independents):
    # Create a scatter plot
    fig = go.Figure()

    # Add scatter traces
    for variable in independents:
        fig.add_trace(go.Scatter(x=dataframe[variable], y=dataframe[dependent], mode='markers', name=variable))

    # Layout settings
    fig.update_layout(title='Scatter Plots of dependent vs. independents',
                      xaxis_title='dependents',
                      yaxis_title=dependent)

    # Display the plot using st.plotly_chart
    st.plotly_chart(fig)

@st.cache_data
def variable_list(dependent,independents):
    return [dependent, independents]


def main():
    st.set_page_config(page_title="Moby - Data prep")
    st.title('Data prep')

    with st.form("choose_file"):
        boolean0 = 'raw_data' not in list(st.session_state.keys())
        if boolean0:
            st.title('file upload')
            file = st.file_uploader('Choose file')
        submit = st.form_submit_button("Submit")
        # if the file was loaded
        if boolean0 and submit:
            if file:
                # read the file into df
                file_read = read_any(file)
                column_names = list(file_read.columns.values)
                st.session_state.update({'col_names': column_names,
                                         'raw_data': file_read,
                                         'path': get_folder_from_path(os.path.abspath(__file__))[0]})
                st.dataframe(file_read.head())
                st.write("shape: ", file_read.shape)

    with st.form("create_folder"):
        st.title("create folder ")
        boolean1 = 'path' in list(st.session_state.keys())
        if boolean1:
            path = st.session_state.get('path')
            value = 'my_project'
            out_path = st.text_input('Create a working folder :',
                                     value=path + delimiter + value)
        submit = st.form_submit_button("Submit")
        if submit and boolean1:
            try:
                os.makedirs(name=out_path)
            except FileExistsError:
                st.write("Folder already exists")
            st.session_state.update({'out_path': out_path})

    with st.form("select_variables"):
        st.title("choose variables")
        boolean2 = 'col_names' in list(st.session_state.keys())
        if boolean2:
            column_names = st.session_state.get('col_names')
            if 'dependent' not in list(st.session_state.keys()):
                dependent = st.selectbox("Select dependent :",
                                         options=column_names)
            else:
                dependent = st.selectbox("Select dependent :",
                                         options=column_names,
                                         index=column_names.index(st.session_state.get('dependent')))

            if 'independents' not in list(st.session_state.keys()):
                independents = st.multiselect("Select independents :",
                                              options=column_names)
            else:
                independents = st.multiselect("Select independents :",
                                              options=column_names,
                                              default=st.session_state.get('independents'))

        submitted = st.form_submit_button("Submit")
        if submitted and boolean2:
            if dependent in independents:
                independents.pop(independents.index(dependent))
            file_read = st.session_state.get('raw_data')
            selected_data = file_read[[dependent] + independents]
            st.session_state.update({'data': selected_data,
                                     'dependent': dependent,
                                     'independents': independents})
            st.dataframe(selected_data.head())
            st.write("shape: ",selected_data.shape)
            plot(selected_data, dependent, independents)

    with st.form("transformations"):
        st.title("transformations")
        boolean3 = 'data' in list(st.session_state.keys())
        if boolean3:
            all_vars = [dependent] + independents
            transformations = ['lag', 'return', 'diff']
            data = {'transformation': transformations}
            for var in all_vars:
                data.update({var: [0.0, 0.0, 0.0]})

            df = pd.DataFrame(data=data)
            gb = GridOptionsBuilder.from_dataframe(df)
            for var in all_vars:
                gb.configure_column(var, editable=True, cellRenderer=valuebox_renderer)

            st.write('Enter the values for transformations and Submit to update')
            ag = AgGrid(
                df,
                gridOptions=gb.build(),
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False,
            )

        submitted = st.form_submit_button("Submit")
        if submitted and boolean3:
            new_data = ag['data']
            st.write('updated transformation values')
            st.dataframe(new_data)
            # make a copy of the selected_Data
            data_copy = st.session_state.get('data').copy()
            # select transformations and transform the data
            for var in all_vars:
                for trans in transformations:
                    trans_value = int(new_data.loc[new_data.transformation == trans, var])
                    if trans_value != 0:
                        if trans == 'lag':
                            data_copy.loc[:,var] = data_copy[var].shift(trans_value)
                        if trans == 'return':
                            data_copy.loc[:,var] = data_copy[var].pct_change(trans_value) + 1
                        if trans == 'diff':
                            data_copy.loc[:,var] = data_copy[var].diff(trans_value)

            st.session_state.update({'trans': ag['data']})
            st.session_state.update({'transformed_data': data_copy})
            st.dataframe(data_copy)
            st.write(data_copy.shape)
            plot(data_copy, dependent, independents)

    with st.form("save_outputs1"):
        st.title('save outputs')
        boolean4 = 'transformed_data' in list(st.session_state.keys())
        boolean5 = 'out_path' in list(st.session_state.keys())
        if boolean4:
            if boolean5:
                out_path = st.session_state.get('out_path')
                st.write('Click to save files here :', out_path)
            else:
                st.write('An output folder does not exist, you can lose all your work.')
                st.write('Please create one using the form at the top of the page.')

        button = st.form_submit_button('Go')
        if button and boolean4 and boolean5:
            try:
                st.session_state.get('trans').to_csv(out_path + 'transformations_applied.csv')
                st.session_state.get('transformed_data').to_csv(out_path + 'transformed_data.csv')
                st.write('files_saved')
            except FileNotFoundError:
                st.write("Error : please check all the above steps.")
    with st.form("further treatment of the data"):
        # this would include treatment of missing data and
        # selection of rows based on a condition being satisfied.

        pass


if __name__ == "__main__":
    main()