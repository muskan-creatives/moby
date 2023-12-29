import streamlit as st
from src.aux import exists, get, update
from streamlit_extras.switch_page_button import switch_page


def main():
    st.set_page_config(page_title="Moby - Sampling")
    st.title('Sampling')
    st.session_state.update({'sampling': False})

    st.text_area('Guidance',
                 'By default, the whole data set will be considered in-sample unless OOS/OOT are chosen.'
                 'The OOT shall be chosen based on a fixed percentage from the temporal head or tail of the data'
                 'In case of OOS, user can also select variables based on which stratification can be done, these'
                 ' variables will then be binned into classes automatically for the purpose if a separate binned column'
                 ' has not been provided. sampling or stratification for a data where the smallest bin has fewer than'
                 ' 30 members may lead to volatile estimates.',
                 height=160)

    with st.form("proceed_to_model_build_without_sampling (must be selected using button to proceed)"):
        sample_cache = get('sampling')
        no_sample = st.checkbox("Proceed to model build without sampling: ", value=sample_cache)
        submit = st.form_submit_button("Go")
        if submit:
            if no_sample:
                update('dev_data', get('treated_data'))
                switch_page('model')
            else:
                update('sampling', True)

    with st.form("OOS or OOT"):
        sample_cache = get('sampling')
        toggle = st.selectbox("sampling type",options=['OOS', 'OOT'], index=0)
        submit = st.form_submit_button("Go", disabled=(not sample_cache))
        if submit and (not sample_cache):
            update('OOS_OOT', toggle)
        else:
            if exists('OOS_OOT'):
                del st.session_state['OOS_OOT']


if __name__ == "__main__":
    main()