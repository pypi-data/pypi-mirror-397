from lib.commons_metrics.commons_metrics import DatabaseConnection, Util, ComponentRepository


def get_connection_database_from_secret(secret_name: str, logger: str, aws_region: str) -> ComponentRepository:
    """
    Retrieve connection database from AWS secrets manager
    """
    secret_json = Util.get_secret_aws(secret_name, logger, aws_region)
    db_connection = DatabaseConnection()
    db_connection.connect({
        'host': secret_json["host"],
        'port': secret_json["port"],
        'dbname': secret_json["dbname"],
        'username': secret_json["username"],
        'password': secret_json["password"]
    })

    return ComponentRepository(db_connection)
