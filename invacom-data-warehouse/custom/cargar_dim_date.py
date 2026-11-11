import pandas as pd
from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_dim_date(*args, **kwargs):
    # Conexión al Data Warehouse (dw_invacom)
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    # Generar rango de fechas desde 1995 hasta 2025
    fechas = pd.date_range(start='1995-01-01', end='2025-12-31', freq='D')

    df = pd.DataFrame({'fecha': fechas})

    # Diccionarios para nombres en español
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    dias_es = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }

    # Calcular los atributos requeridos por la tabla dim.dim_date
    df['id_date'] = df['fecha'].dt.strftime('%Y%m%d').astype(int)
    df['anio'] = df['fecha'].dt.year
    df['trimestre'] = df['fecha'].dt.quarter
    df['mes'] = df['fecha'].dt.month
    df['nombre_mes'] = df['mes'].map(meses_es)
    df['dia'] = df['fecha'].dt.day
    # En SQL Server dia_semana sera aquí 1=Lunes .. 7=Domingo
    df['dia_semana'] = df['fecha'].dt.dayofweek + 1
    df['nombre_dia'] = df['fecha'].dt.dayofweek.map(dias_es)
    df['semana_anio'] = df['fecha'].dt.isocalendar().week.astype(int)
    df['fecha'] = df['fecha'].dt.date

    # Reordenar columnas según la definición de dim.dim_date
    columnas = [
        'id_date', 'fecha', 'anio', 'trimestre', 'mes',
        'nombre_mes', 'dia', 'dia_semana', 'nombre_dia', 'semana_anio'
    ]
    df = df[columnas]

    # Vaciar y cargar en dw_invacom.dim.dim_date
    with motor.begin() as conn:
        conn.execute(text('DELETE FROM dim.dim_date'))
        df.to_sql(
            'dim_date',
            conn,
            schema='dim',
            if_exists='append',
            index=False,
            chunksize=2000,
        )

    motor.dispose()
    print(f"Éxito: {len(df):,} fechas cargadas en dim.dim_date.")
    return len(df)