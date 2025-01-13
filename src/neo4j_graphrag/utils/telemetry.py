import neo4j
from neo4j_graphrag import __version__


# Override user-agent used by neo4j package so we can measure usage of the package by version
def override_user_agent(driver: neo4j.Driver) -> neo4j.Driver:
    driver._pool.pool_config.user_agent = f"neo4j-graphrag-python/v{__version__}"
    return driver
