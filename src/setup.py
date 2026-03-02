import ezyquant as ez


def setup(database_path: str):
    ez.connect_sqlite(database_path)
