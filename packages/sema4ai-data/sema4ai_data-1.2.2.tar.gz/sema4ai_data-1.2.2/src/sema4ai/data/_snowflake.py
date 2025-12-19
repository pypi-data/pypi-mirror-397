import os
from contextlib import closing, contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from sema4ai.actions import ActionError

if TYPE_CHECKING:
    import snowflake.connector

import snowflake.connector  # type: ignore[import-not-found]

from sema4ai.data._config import _get_snowflake_connection_details_from_file

_SPCS_TOKEN_FILE_PATH = Path("/snowflake/session/token")
_LOCAL_AUTH_FILE_PATH = Path.home() / ".sema4ai" / "sf-auth.json"


class SnowflakeAuthenticationError(ActionError):
    """Raised when there are authentication-related issues with Snowflake connection."""

    pass


snowflake.connector.paramstyle = "numeric"


def get_snowflake_connection_details(
    role: str | None = None,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
) -> dict:
    """
    Get Snowflake connection details based on the environment.

    This function first checks if running in SPCS by looking for the token file.
    If found, it uses SPCS authentication, otherwise falls back to local config-based authentication.

    Args:
        role: Snowflake role to use. Falls back to env var
        warehouse: Snowflake warehouse to use. Falls back to env var
        database: Snowflake database to use. Falls back to env var
        schema: Snowflake schema to use. Falls back to env var

    Returns:
        dict: Connection credentials for Snowflake containing environment-specific fields:
            For SPCS:
               host: from SNOWFLAKE_HOST env var
               account: from SNOWFLAKE_ACCOUNT env var
               authenticator: "OAUTH"
               token: from SPCS token file
               role, warehouse, database, schema: from args or env vars
               client_session_keep_alive: True
               port: from SNOWFLAKE_PORT env var
               protocol: "https"
            For local machine:
               account: from config
               authenticator: from config (OAUTH, or SNOWFLAKE_JWT)
               user: from config (only for SNOWFLAKE_JWT)
               token: from config (only for OAUTH)
               role: from args or config
               warehouse: from args or config
               database, schema: from args
               client_session_keep_alive: True
               private_key and private_key_password (only for SNOWFLAKE_JWT)

    Raises:
        SnowflakeAuthenticationError: If required credentials are missing or invalid
    """

    # Check for SPCS environment first
    if is_running_in_spcs():
        token = _SPCS_TOKEN_FILE_PATH.read_text().strip()

        host = os.getenv("SNOWFLAKE_HOST")
        account = os.getenv("SNOWFLAKE_ACCOUNT")

        if not host or not account:
            raise SnowflakeAuthenticationError(
                "Required environment variables SNOWFLAKE_HOST and SNOWFLAKE_ACCOUNT must be set"
            )

        return {
            "host": host,
            "account": account,
            "authenticator": "OAUTH",
            "token": token,
            "role": role or os.getenv("SNOWFLAKE_ROLE"),
            "warehouse": warehouse or os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": database or os.getenv("SNOWFLAKE_DATABASE"),
            "schema": schema or os.getenv("SNOWFLAKE_SCHEMA"),
            "client_session_keep_alive": True,
            "port": os.getenv("SNOWFLAKE_PORT"),
            "protocol": "https",
        }

    # Fall back to localhost config file based authentication
    try:
        return _get_snowflake_connection_details_from_file(
            _LOCAL_AUTH_FILE_PATH, role, warehouse, database, schema
        )
    except Exception as e:
        raise SnowflakeAuthenticationError(
            f"Failed to read authentication config from {_LOCAL_AUTH_FILE_PATH}: {str(e)}"
        ) from e


def is_running_in_spcs() -> bool:
    """
    Code is currently running in Snowpark Container Services (SPCS) if token file exists.
    """
    return _SPCS_TOKEN_FILE_PATH.exists()


def _extract_snowflake_rest_token(
    connection: "snowflake.connector.SnowflakeConnection",
) -> str | None:
    """
    Retrieve the primary REST token from a Snowflake connector connection object.

    Args:
        connection: A Snowflake connector connection object
                    that has a REST connection with a token attribute.

    Returns:
        The REST token string, or None if not available.

    Raises:
        ValueError: If no REST connection is found on the connection object.
    """
    rest_connection = getattr(connection, "rest", None)
    if rest_connection is None:
        raise ValueError("No REST connection found for Snowflake connection object")
    token = getattr(rest_connection, "token", None)
    if token:
        return token
    return None


def get_snowflake_rest_api_headers(
    connection: "snowflake.connector.SnowflakeConnection",
) -> dict[str, str]:
    """
    Get HTTP headers for making REST API calls to Snowflake (e.g., Cortex APIs).

    This function automatically detects the environment (SPCS vs local) and constructs
    the appropriate authentication headers.

    Args:
        connection: A Snowflake connector connection object.
                   Required for local environments to extract the REST token.
                   Can be None if running in SPCS.

    Returns:
        A dictionary of HTTP headers including:
        - Authorization: Bearer token (SPCS) or Snowflake Token format (local)
        - X-Snowflake-Authorization-Token-Type: "OAUTH" (only for SPCS)
        - Content-Type: "application/json"

    Raises:
        SnowflakeAuthenticationError: If running in SPCS and required files/env vars are missing
        ValueError: If running locally and connection object doesn't have REST token access
    """
    headers: dict[str, str] = {
        "Content-Type": "application/json",
    }

    # Check if running in SPCS environment
    if is_running_in_spcs():
        token = _SPCS_TOKEN_FILE_PATH.read_text().strip()
        headers["Authorization"] = f"Bearer {token}"
        headers["X-Snowflake-Authorization-Token-Type"] = "OAUTH"
    else:
        # Local environment - extract token from connection object
        if connection is None:
            raise ValueError(
                "Connection object is required for local environments to extract REST token"
            )
        rest_token: str | None = _extract_snowflake_rest_token(connection)
        if rest_token is None:
            raise ValueError("Unable to extract REST token from connection object")
        # After None check, rest_token is guaranteed to be str
        headers["Authorization"] = f'Snowflake Token="{rest_token}"'

    return headers


def get_snowflake_cortex_api_base_url(
    connection: "snowflake.connector.SnowflakeConnection", endpoint: str
) -> str:
    """
    Get the base URL for Snowflake Cortex API endpoints.

    This function automatically detects the environment (SPCS vs local) and constructs
    the appropriate base URL for Cortex API calls.

    Args:
        connection: A Snowflake connector connection object.
                   Required for local environments to get account name.
                   Can be None if running in SPCS.
        endpoint: The API endpoint path (e.g., "/api/v2/cortex/analyst/message").

    Returns:
        The full base URL for the Cortex API endpoint.

    Raises:
        SnowflakeAuthenticationError: If running in SPCS and required env vars are missing
        ValueError: If running locally and connection object is None
    """
    # Ensure endpoint starts with '/'
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    if is_running_in_spcs():
        snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
        snowflake_host = os.getenv("SNOWFLAKE_HOST")

        if not snowflake_host or not snowflake_account:
            raise SnowflakeAuthenticationError(
                "Required environment variables SNOWFLAKE_HOST and SNOWFLAKE_ACCOUNT must be set"
            )

        # Handle case where host starts with "snowflake." placeholder
        if snowflake_host.startswith("snowflake."):
            snowflake_host = snowflake_host.replace(
                "snowflake", snowflake_account.lower().replace("_", "-"), 1
            )

        return f"https://{snowflake_host}{endpoint}"
    else:
        # Local environment - use connection account
        if connection is None:
            raise ValueError(
                "Connection object is required for local environments to determine account"
            )
        account = connection.account.replace("_", "-")
        return f"https://{account}.snowflakecomputing.com{endpoint}"


@contextmanager
def get_snowflake_connection(
    role: str | None = None,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
):
    """
    Get a Snowflake connection as a context manager with automatic cleanup.

    This function creates a connection using the authentication method appropriate
    for the environment (SPCS or local config), sets up the connection properly,
    and ensures it's closed when exiting the context.

    Args:
        role: Snowflake role to use. Falls back to env var or config.
        warehouse: Snowflake warehouse to use. Falls back to env var or config.
        database: Snowflake database to use. Falls back to env var or config.
        schema: Snowflake schema to use. Falls back to env var or config.

    Yields:
        A Snowflake connection object (snowflake.connector.SnowflakeConnection).

    Raises:
        SnowflakeAuthenticationError: If connection details cannot be obtained.
        ImportError: If snowflake-connector-python is not installed.

    Example:
        ```python
        from sema4ai.data import get_snowflake_connection

        with get_snowflake_connection(database="MYDB", schema="MYSCHEMA") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM my_table")
            results = cursor.fetchall()
        ```
    """
    # snowflake.connector is imported at module load; paramstyle set globally
    config = get_snowflake_connection_details(
        role=role, warehouse=warehouse, database=database, schema=schema
    )

    conn = None
    try:
        conn = snowflake.connector.connect(**config)
        yield conn
    finally:
        if conn:
            conn.close()


def execute_snowflake_query(
    query: str,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
    role: str | None = None,
    numeric_args: list | None = None,
) -> list[dict]:
    """
    Execute a SQL query against Snowflake and return results as a list of dictionaries.

    This function handles connection management, sets the warehouse/database/schema context,
    executes the query with numeric parameters (Snowflake style :1, :2, etc.), and formats
    results appropriately (handles both Arrow and traditional result formats).

    Args:
        query: The SQL query to execute.
        warehouse: Snowflake warehouse to use. Falls back to env var or config.
        database: Snowflake database to use. Falls back to env var or config.
        schema: Snowflake schema to use. Falls back to env var or config.
        role: Snowflake role to use. Falls back to env var or config.
        numeric_args: A list of parameters to pass to the query (used with :1, :2 placeholders).

    Returns:
        A list of dictionaries, where each dictionary represents a row with column names as keys.

    Raises:
        SnowflakeAuthenticationError: If connection details cannot be obtained.
        ImportError: If snowflake-connector-python is not installed.
        ValueError: If there are issues with warehouse, database, schema, or query execution.
            Enhanced error messages are provided with context and common issues.

    Example:
        ```python
        from sema4ai.data import execute_snowflake_query

        results = execute_snowflake_query(
            query="SELECT name, age FROM users WHERE id = :1",
            warehouse="MY_WH",
            database="MY_DB",
            schema="MY_SCHEMA",
            numeric_args=[123]
        )
        # Returns: [{"name": "John", "age": 30}]
        ```
    """
    import pandas as pd  # type: ignore[import-not-found]

    numeric_args = numeric_args or []
    # paramstyle set at module import

    with get_snowflake_connection(
        role=role, warehouse=warehouse, database=database, schema=schema
    ) as conn, closing(conn.cursor()) as cursor:
        try:
            if warehouse:
                cursor.execute(f'USE WAREHOUSE "{warehouse.upper()}"')
        except snowflake.connector.errors.ProgrammingError as e:
            raise ValueError(
                f"Failed to use warehouse '{warehouse}'. "
                f"Error: {str(e)}\n"
                f"Common issues:\n"
                f"  - Warehouse does not exist\n"
                f"  - Insufficient permissions to use this warehouse\n"
                f"  - Warehouse name is misspelled"
            ) from e

        try:
            if database:
                cursor.execute(f'USE DATABASE "{database.upper()}"')
        except snowflake.connector.errors.ProgrammingError as e:
            raise ValueError(
                f"Failed to use database '{database}'. "
                f"Error: {str(e)}\n"
                f"Common issues:\n"
                f"  - Database does not exist\n"
                f"  - Insufficient permissions to access this database\n"
                f"  - Database name is misspelled"
            ) from e

        try:
            if schema:
                cursor.execute(f'USE SCHEMA "{schema.upper()}"')
        except snowflake.connector.errors.ProgrammingError as e:
            raise ValueError(
                f"Failed to use schema '{schema}'. "
                f"Error: {str(e)}\n"
                f"Common issues:\n"
                f"  - Schema does not exist\n"
                f"  - Insufficient permissions to access this schema\n"
                f"  - Schema name is misspelled"
            ) from e

        try:
            cursor.execute(query, numeric_args)
        except snowflake.connector.errors.ProgrammingError as e:
            error_msg = str(e).lower()

            # Enhance error messages with context (in case error occurred during query execution)
            if "warehouse" in error_msg or "use warehouse" in error_msg.lower():
                raise ValueError(
                    f"Failed to use warehouse '{warehouse}'. "
                    f"Error: {str(e)}\n"
                    f"Common issues:\n"
                    f"  - Warehouse does not exist\n"
                    f"  - Insufficient permissions to use this warehouse\n"
                    f"  - Warehouse name is misspelled"
                ) from e
            elif "database" in error_msg or "use database" in error_msg.lower():
                raise ValueError(
                    f"Failed to use database '{database}'. "
                    f"Error: {str(e)}\n"
                    f"Common issues:\n"
                    f"  - Database does not exist\n"
                    f"  - Insufficient permissions to access this database\n"
                    f"  - Database name is misspelled"
                ) from e
            elif "schema" in error_msg or "use schema" in error_msg.lower():
                raise ValueError(
                    f"Failed to use schema '{schema}'. "
                    f"Error: {str(e)}\n"
                    f"Common issues:\n"
                    f"  - Schema does not exist\n"
                    f"  - Insufficient permissions to access this schema\n"
                    f"  - Schema name is misspelled"
                ) from e
            else:
                raise ValueError(
                    f"Failed to execute query. "
                    f"Error: {str(e)}\n"
                    f"Query: {query}\n"
                    f"Common issues:\n"
                    f"  - Table or view does not exist\n"
                    f"  - SQL syntax error\n"
                    f"  - Insufficient permissions to access the objects\n"
                    f"  - Object names are misspelled"
                ) from e

        if cursor._query_result_format == "arrow":
            results = cursor.fetch_pandas_all()
            return (
                results.astype(object).where(pd.notnull, None).to_dict(orient="records")
            )
        else:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            return result
