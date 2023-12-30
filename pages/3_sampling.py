import streamlit as st
from src.aux import exists, get, update
from src.sample import oos_data, oot_data
from streamlit_extras.switch_page_button import switch_page

IN_SAMPLE_MIN = 50
IN_SAMPLE_DEF = 70


def main():
    st.set_page_config(page_title="Moby - Sampling")
    st.title('Sampling')
    st.sidebar.success("Components")
    update('sampling', False)

    bool_oos = (True if get('OOS_OOT') == 'OOS' else False) if exists('OOS_OOT') else False
    bool_oot = (True if get('OOS_OOT') == 'OOT' else False) if exists('OOS_OOT') else False

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
                switch_page('model')
            else:
                update('sampling', True)

    with st.form("OOS or OOT"):
        st.title("sampling type")
        toggle = st.selectbox("", options=['OOS', 'OOT'], index=0)
        submit = st.form_submit_button("Go", disabled=(not get('sampling')))
        if submit:
            update('OOS_OOT', toggle)
            bool_oos = True if toggle == 'OOS' else False
            bool_oot = not bool_oos

    with st.form("OOS specifications"):
        st.title("Out of sample:")
        in_sample_default = get('in_sample_pct') if exists('in_sample_pct') else IN_SAMPLE_DEF
        default_strata: list = get('sample_strata') if exists('sample_strata') else []
        options = get('independents') if exists('independents') else []
        in_sample_pct = st.slider("in-sample percentage", IN_SAMPLE_MIN, 100, in_sample_default)
        sample_strata = st.multiselect("select variables to stratify based on:",
                                       options=options,
                                       default=default_strata)
        # a function will now return indices for in and out of sample data sets
        # based on input data and strata fields.
        submit = st.form_submit_button("Go", disabled=not (exists('OOS_OOT') and bool_oos))
        if submit:
            in_oos_index, out_oos_index = oos_data(data=get('treated_data'),
                                                   strata_cols=sample_strata,
                                                   in_sample_pct=float(in_sample_pct/100))
            update('in_oos_index', in_oos_index)
            update('out_oos_index', out_oos_index)
            switch_page('model')

    with st.form("OOT specifications"):
        st.title("Out of time:")
        oot_from_tail = get('oot_from_tail') if exists('oot_from_tail') else True
        in_sample_pct = st.slider("in-sample percentage", IN_SAMPLE_MIN, 100, in_sample_default)
        submit = st.form_submit_button("Go", disabled=not (exists('OOS_OOT') and bool_oot))
        if submit:
            in_oot_index, out_oot_index = oot_data(data=get('treated_data'),
                                                   in_sample_pct=(in_sample_pct/100),
                                                   tail=oot_from_tail)
            update('in_oot_index', in_oot_index)
            update('out_oot_index', out_oot_index)
            switch_page('model')


if __name__ == "__main__":
    main()
