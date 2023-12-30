# model build functions

import numpy as np
import statsmodels.api as sm
from src.aux import get


def ols():
    data = get('treated_data')
    dependent, independents = get('dependent'), get('independents')
    in_sample_index, out_sample_index = get('in_oos_index'), get('out_oos_index')
    Y_dev, X_dev = data[[dependent]].iloc[in_sample_index], data[independents].iloc[in_sample_index]
    Y_test, X_test = data[[dependent]].iloc[out_sample_index], data[independents].iloc[out_sample_index]
    X_dev, X_test = sm.add_constant(X_dev), sm.add_constant(X_test)
    model = sm.OLS(Y_dev, X_dev)
    results = model.fit()
    pred = results.predict(X_test)
    oos_mse = np.mean((Y_test.values - pred.values)**2)
    return results, (Y_dev, X_dev), (Y_test, X_test), pred, oos_mse
