import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from src.input_output import read_any
from src.aux import exists, get, update
from src.aux import get_folder_from_path, delimiter, valuebox_renderer
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_extras.switch_page_button import switch_page

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
        boolean0 = not exists('raw_data')
        if boolean0:
            st.title('file upload')
            file = st.file_uploader('Choose file')
            disabled = False
        else:
            disabled = True
        submit = st.form_submit_button("Submit", disabled=disabled)
        # if the file was loaded
        if boolean0 and submit:
            if file:
                # read the file into df
                file_read = read_any(file)
                column_names = list(file_read.columns.values)
                update('col_names', column_names)
                update('raw_data', file_read)
                update('path',get_folder_from_path(os.path.abspath(__file__))[0])
                st.dataframe(file_read.head())
                st.write("shape: ", file_read.shape)

    with st.form("create_folder"):
        st.title("create folder ")
        boolean1 = exists('path')
        if boolean1:
            path = get('path')
            value = 'my_project'
            out_path = st.text_input('Create a working folder :',
                                     value=path + delimiter + value)
        submit = st.form_submit_button("Submit")
        if submit and boolean1:
            try:
                os.makedirs(name=out_path)
            except FileExistsError:
                st.write("Folder already exists")
            update('out_path', out_path)

    with st.form("select_variables"):
        st.title("choose variables")
        boolean2 = exists('col_names')
        if boolean2:
            column_names = get('col_names')
            if not exists('dependent'):
                dependent = st.selectbox("Select dependent :",
                                         options=column_names)
            else:
                dependent = st.selectbox("Select dependent :",
                                         options=column_names,
                                         index=column_names.index(get('dependent')))

            if not exists('independents'):
                independents = st.multiselect("Select independents :",
                                              options=column_names)
            else:
                independents = st.multiselect("Select independents :",
                                              options=column_names,
                                              default=get('independents'))

        submitted = st.form_submit_button("Submit")
        if submitted and boolean2:
            if dependent in independents:
                independents.pop(independents.index(dependent))
            file_read = get('raw_data')
            all_vars = [dependent] + independents
            selected_data = file_read[all_vars]

            update('data', selected_data)
            update('dependent', dependent)
            update('independents', independents)
            update('all_vars', all_vars)

            st.dataframe(selected_data.head())
            st.write("shape: ",selected_data.shape)
            plot(selected_data, dependent, independents)

    with st.form("transformations"):
        st.title("transformations")
        boolean3 = exists('data')
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
            data_copy = get('data').copy()
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

            update('trans', ag['data'])
            update('transformed_data', data_copy)

            st.dataframe(data_copy)
            st.write(data_copy.shape)
            plot(data_copy, dependent, independents)

    with st.form("further treatment of the data"):
        st.title("treatments")
        # this would include treatment of missing data and
        # selection of rows based on a condition being satisfied.
        boolean4 = exists('transformed_data')
        if boolean4:
            st.write("treatment of NAs")
            drop_na = st.checkbox("drop_NA", value=True)
            replace_na = st.number_input("replace NAs with: ",)
            st.divider()

            st.write("drop rows for any value NOT in between")
            select_vars = st.multiselect("choose_variables: ", options=get('all_vars'))
            col1, col2, _ = st.columns([1, 1, 5])
            range1 = col1.text_input("from")
            range2 = col2.text_input("to")

            st.divider()
            st.write("drop rows for values equal to")
            range3 = st.text_input("drop rows for any value equal to: (separate values with commas) ")
            drop_by_text = st.text_input("drop rows which have the text: (only one value)")

            st.divider()
        button = st.form_submit_button('Go')
        if button and boolean4:
            trans_data = get('transformed_data').copy()
            if drop_na:
                trans_data.dropna(inplace=True, ignore_index=True)
                update('na_treatment', 'drop')
                update('na_fill', 'None')
            else:
                trans_data.fillna(value=replace_na, inplace=True, ignore_index=True)
                update('na_treatment', 'fill')
                update('na_fill', replace_na)

            if select_vars and (range1 or range2):
                if not range1:
                    range2 = eval(range2)
                    range1 = -np.inf
                else:
                    range1 = eval(range1)
                    range2 = np.inf
                # the cells which are in the range
                condition = (trans_data[select_vars].values >= range1) | \
                            (trans_data[select_vars].values <= range2)
                # retain only these rows
                trans_data.drop(np.where(condition.any(axis=1)), inplace=True)
                trans_data.reset_index(inplace=True)
                update('range_selection', True)
                update('range', [range1, range2])

            if range3:
                # split text into distinct values
                list_of_texts = (((range3.split('['))[1].split(']'))[0]).split(',')
                list_of_numbers = [eval(i) for i in list_of_texts]
                for element in list_of_numbers:
                    trans_data.drop(np.where((trans_data.values == element).any(axis=1)))
                    trans_data.reset_index(inplace=True)
                update('drop_variables_by_values', list_of_numbers)

            if drop_by_text:
                trans_data.drop(np.where((trans_data.values == drop_by_text).any(axis=1)))
                trans_data.reset_index(inplace=True)
                update('drop_variables_by_text', drop_by_text)

            update('treated_data', trans_data)
            st.write("treated data:")
            st.dataframe(trans_data)

    with st.form("save_outputs1"):
        st.title('save outputs')
        boolean5 = exists('treated_data')
        boolean6 = exists('out_path')
        if boolean5:
            if boolean6:
                out_path = get('out_path')
                st.write('Click to save files here :', out_path)
            else:
                st.write('An output folder does not exist, you can lose all your work.')
                st.write('Please create one using the form at the top of the page.')

        button = st.form_submit_button('Go')
        if button and boolean5 and boolean6:
            try:
                get('trans').to_csv(out_path + delimiter + 'transformations_applied.csv')
                treatment_file = {'title': 'file to store the treatments applied to the data'}
                treatments = ['na_treatment', 'na_fill', 'range_selection', 'range',
                              'drop_variables_by_values', 'drop_variables_by_text']
                for treatment in treatments:
                    if exists(treatment):
                        treatment_file.update({treatment: get(treatment)})
                with open(out_path + delimiter + 'treatments.json', 'w') as f:
                    json.dump(treatment_file, f)
                get('transformed_data').to_csv(out_path + delimiter + 'transformed_data.csv')
                get('treated_data').to_csv(out_path + delimiter + 'treated_data.csv')
                update('files_saved', True)
                st.write('files_saved')
            except FileNotFoundError:
                st.write("Error : please check all the above steps.")
        else:
            update('files_saved', False)

    with st.form("proceed_to_model_build"):
        st.write('Click to proceed to sampling')
        button = st.form_submit_button('Go')
        if button:
            switch_page('sampling')


if __name__ == "__main__":
    main()