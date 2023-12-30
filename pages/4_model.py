import streamlit as st
from src.aux import get, exists, update
from src.model_build import ols

# models where prior sampling is needed
MODELS_S = ['OLS']  # 'LOGISTIC' etc to be added later
MODELS_NS = ['LASSO']  # 'LASSO', 'RIDGE', 'ELASTIC_NET' etc to be added where CV is done inherently
MODELS = MODELS_S + MODELS_NS


def main():
    st.set_page_config(page_title="Moby - model")
    st.title('Modelling')
    st.sidebar.success("Components")

    with st.form("model_type_choice"):
        st.title("Model type")
        if exists('sampling') and exists('OOS_OOT'):
            opt = MODELS
        else:
            opt = MODELS_S
        model_type = st.selectbox("select model type:",
                                  options=opt,
                                  index=opt.index(get('model_type')) if exists('model_type') else 0)
        submit = st.form_submit_button("Go")
        if submit:
            update('model_type', model_type)

    with st.form("OLS"):
        st.title("OLS")
        bool_OLS = get('model_type') == 'OLS' if exists('model_type') else False
        submit = st.form_submit_button("Run OLS", disabled=not bool_OLS)
        if submit:
            res, (Y_dev, X_dev), (Y_test, X_test), pred, oos_mse = ols()
            st.write(res.summary())
            st.write('sample mse', res.mse_resid)
            st.write('test mse', oos_mse)


if __name__ == "__main__":
    main()
