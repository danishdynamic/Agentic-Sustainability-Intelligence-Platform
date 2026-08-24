from langgraph.checkpoint.memory import MemorySaver

_postgres_context = None


def checkpointer():
    global _postgres_context
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from app.config.settings import get_settings

        if _postgres_context is None:
            _postgres_context = PostgresSaver.from_conn_string(
                get_settings().database_url
            )
        saver = _postgres_context.__enter__()
        saver.setup()
        return saver
    except (ImportError, Exception):
        return MemorySaver()
