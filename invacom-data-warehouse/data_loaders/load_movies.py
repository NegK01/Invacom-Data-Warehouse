import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    # Ruta al archivo de películas descomprimido
    file_path = r'ml-25m/movies.csv'
    df = pd.read_csv(file_path)
    return df


@test
def test_output(output, *args) -> None:
    assert output is not None, 'La salida no está definida'
    assert len(output) > 0, 'No se cargó ninguna película'