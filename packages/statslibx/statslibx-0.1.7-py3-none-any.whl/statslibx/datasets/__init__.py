from typing import Optional, Union, Literal, List
import polars as pl
import pandas as pd
import pkgutil
import io

def load_dataset(
        name: str,
        backend: Literal['pandas', 'polars'] = 'pandas'
    ) -> Union[pd.DataFrame, pl.DataFrame]:
    """Carga un dataset interno del paquete.
    Datasets Disponibles:
    - iris.csv
    - penguins.csv
    - sp500_companies.csv
    - titanic.csv
    - course_completion.csv
    """
    data_bytes = pkgutil.get_data("statslibx.datasets", name)
    if data_bytes is None:
        raise FileNotFoundError(f"Dataset '{name}' no encontrado.")
    
    if backend == "pandas":
        return pd.read_csv(io.BytesIO(data_bytes))
    elif backend == "polars":
        return pl.read_csv(io.BytesIO(data_bytes))
    else:
        raise ValueError(
            "Backend no soportado. Use 'pandas' o 'polars'."
        )
    
def load_iris(
        backend: Literal['pandas', 'polars'] = 'pandas'
    ) -> Union[pd.DataFrame, pl.DataFrame]:
    """Carga el dataset interno de la libreria: Iris
    """
    data_bytes = pkgutil.get_data("statslibx.datasets", "iris.csv")
    if data_bytes is None:
        raise FileNotFoundError(f"Dataset \"iris.csv\" no encontrado.")
    
    if backend == "pandas":
        return pd.read_csv(io.BytesIO(data_bytes))
    elif backend == "polars":
        raise ValueError(
            "Backend no soportado aun. Use 'pandas'."
        )
    else:
        raise ValueError(
            "Backend no soportado. Use 'pandas' o 'polars'."
        )
    
def load_penguins(
        backend: Literal['pandas', 'polars'] = 'pandas'
    ) -> Union[pd.DataFrame, pl.DataFrame]:
    """Carga un dataset interno de la libreria: Penguins
    """
    data_bytes = pkgutil.get_data("statslibx.datasets", "penguins.csv")
    if data_bytes is None:
        raise FileNotFoundError(f"Dataset \"penguins.csv\" no encontrado.")
    
    if backend == "pandas":
        return pd.read_csv(io.BytesIO(data_bytes))
    elif backend == "polars":
        raise ValueError(
            "Backend no soportado aun. Use 'pandas'."
        )
    else:
        raise ValueError(
            "Backend no soportado. Use 'pandas' o 'polars'."
        )

