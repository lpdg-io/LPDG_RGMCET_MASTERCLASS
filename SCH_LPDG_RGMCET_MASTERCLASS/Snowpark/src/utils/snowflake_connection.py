import os
from pathlib import Path
from dotenv import load_dotenv
from snowflake.snowpark import Session

def set_env_variables(env='dev'):
    dotenv_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), Path(f'../.env')))
    return load_dotenv(dotenv_path=dotenv_path)


def get_session(env: str = 'dev') -> Session:
    """
    PURPOSE:
        This function gets login information from the
        config file and connects to the
        server. Returns the session object.
    RETURNS:
        A session.
    """

    set_env_variables(env)
    print("try init connection snowflake")
    connection_parameters = {
        "user": os.getenv('SNOWFLAKE_USER'),
        "account": os.getenv('SNOWFLAKE_ACCOUNT'),
        "role": os.getenv('SNOWFLAKE_ROLE'),
        "warehouse": os.getenv('SNOWFLAKE_WH'),
        "database": os.getenv('SNOWFLAKE_DB'),
        "password": os.getenv('SNOWFLAKE_PASSWORD'),
        # "authenticator": os.getenv('SNOWFLAKE_AUTHENTICATOR'),
        "schema": os.getenv('SNOWFLAKE_SCHEMA'),
    }
    print(connection_parameters)
    session = Session.builder.configs(connection_parameters).create()
    return session


def get_current_account_url(session):
    account_url_query = f"""
            SELECT 
            CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME() || '.snowflakecomputing.com' 
            AS ACCOUNT_URL;
            """
    account_url = session.sql(account_url_query).collect()
    return account_url[0]['ACCOUNT_URL']



def get_current_database(session):
    current_db_query = "SELECT CURRENT_DATABASE() AS CURRENT_DB;"
    current_db = session.sql(current_db_query).collect()
    return current_db[0]['CURRENT_DB']