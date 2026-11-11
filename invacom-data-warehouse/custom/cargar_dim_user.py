from sqlalchemy import create_engine, text

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def cargar_dim_user(*args, **kwargs):
    # Conexión al Data Warehouse (dw_invacom)
    motor = create_engine(
        'mssql+pyodbc://@localhost/dw_invacom'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes&TrustServerCertificate=yes',
        fast_executemany=True,
    )

    with motor.begin() as conn:
        # Limpiar la tabla si ya tenía datos
        conn.execute(text('DELETE FROM dim.dim_user'))

        # Reiniciar el contador IDENTITY para que el primer ID vuelva a ser 1
        conn.execute(text('INSERT INTO dim.dim_user (user_id) VALUES (-1)'))
        conn.execute(text('DELETE FROM dim.dim_user WHERE user_id = -1'))
        conn.execute(text("DBCC CHECKIDENT ('dim.dim_user', RESEED, 0)"))

        # Insertar los usuarios únicos desde la vista de Staging
        resultado = conn.execute(text('''
            INSERT INTO dim.dim_user (user_id)
            SELECT user_id
            FROM staging_invacom.stg.v_users
            WHERE user_id IS NOT NULL
            ORDER BY user_id
        '''))

    motor.dispose()
    print(f"Éxito: {resultado.rowcount:,} usuarios cargados en dim.dim_user.")
    return resultado.rowcount