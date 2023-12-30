# functions to create in and out of sample data
from math import ceil
import pandas as pd
from numpy.random import seed, choice


MAX_BINS = 10


def sample(orig_data: pd.DataFrame, in_sample_pct: float):
    data = orig_data.copy()
    if not data.empty and in_sample_pct is not None:
        seed(1234)
        full_index = list(data.index.values)
        size = len(full_index)

        if (in_sample_pct <= 1.0) and (in_sample_pct >= 0.0):
            if size > 1:
                in_sample = choice(full_index,
                                   size=max(1, ceil(in_sample_pct*size)),
                                   replace=False)
                in_sample = list(in_sample)
            else:
                in_sample = full_index
        else:
            in_sample = full_index
        out_sample = list(set(full_index) - set(in_sample))
        return in_sample, out_sample
    else:
        return [], []


def oos_data(data: pd.DataFrame, strata_cols: list, in_sample_pct: float):
    # returns two tuple of indices (in_sample, out_of_sample)
    # if no stratification is required, return simple split.
    if not strata_cols:
        return sample(data, in_sample_pct)
    else:
        # else create groups and sample from groups
        in_sample, out_sample = [], []
        grouping_cols = []
        for var in strata_cols:
            if type(data[var][0]) is not str:
                data[var + '__temp_bin'] = pd.cut(data[var].values, bins=min(MAX_BINS, data.shape[0]))
                grouping_cols.append(var + '__temp_bin')
            else:
                grouping_cols.append(var + '__temp_bin')
        # group by
        df_ = data.groupby(grouping_cols).apply(lambda x: sample(x, in_sample_pct))
        # combine indices
        for ins, outs in df_:
            in_sample += list(ins)
            out_sample += list(outs)
        return in_sample, out_sample


def oot_data(data: pd.DataFrame, in_sample_pct: float, tail: bool):
    # returns two tuple of indices (in_sample, out_of_sample)
    if not data.empty:
        all_indices = list(data.index.values)
        in_size = ceil(in_sample_pct*data.shape[0])
        if tail:
            return list(all_indices[:in_size]),list(all_indices[in_size:])
        else:
            return list(all_indices[in_size:]), list(all_indices[:in_size])
