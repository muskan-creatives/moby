# data set input and modification
import pandas as pd
from src.aux import get_folder_from_path


def read_any(file,output=False,outpath=None):
    if not output:
        extension = ((file.name).split('.'))[-1]
        if extension == "csv":
            return pd.read_csv(file)
        elif extension == "parquet":
            return pd.read_parquet(file)
        elif extension == "sas7bdat":
            return pd.read_sas(file)
        else:
            pass
    else:
        if outpath:
            extension = get_folder_from_path(outpath)[1].split('.')[-1]
            if extension == "csv":
                file.to_csv(outpath)
            elif extension == "parquet":
                return file.to_parquet(outpath)
            else:
                pass
