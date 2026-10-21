import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    # "Toy Story (1995)" -> "1995"
    data['release_year'] = data['title'].str.extract(r'\((\d{4})\)', expand=False)

    # "Toy Story (1995)" -> "Toy Story"
    data['clean_title'] = data['title'].str.replace(r'\s*\(\d{4}\)', '', regex=True).str.strip()

    # Adventure|Animation|Children|Comedy|Fantasy -> Adventure
    data['primary_genre'] = data['genres'].apply(
        lambda x: x.split('|')[0] if pd.notnull(x) and x != '(no genres listed)' else 'Unknown'
    )

    return data


@test
def test_clean_title(output, *args) -> None:
    assert 'clean_title' in output.columns, 'Falta la columna clean_title'
    assert 'release_year' in output.columns, 'Falta la columna release_year'