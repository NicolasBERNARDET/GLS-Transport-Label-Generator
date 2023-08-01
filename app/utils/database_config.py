def get_connection_string(server: str, database: str) -> str:
    return f"DRIVER={{SQL SERVER}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"