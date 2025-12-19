from webscout.Provider.OPENAI import *
try:
    def run_api(*args, **kwargs):
        from webscout.server.server import run_api as _run_api
        return _run_api(*args, **kwargs)
    
    def start_server(**kwargs):
        """Start the Webscout OpenAI-compatible API server (FastAPI backend)."""
        from webscout.server.server import run_api as _run_api
        return _run_api(**kwargs)
except ImportError:
    def run_api(*args, **kwargs):
        raise ImportError("webscout.server.server.run_api is not available in this environment.")
    def start_server(*args, **kwargs):
        raise ImportError("webscout.server.server.start_server is not available in this environment.")