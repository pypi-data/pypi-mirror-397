from redpanda.engine.game import Game
from redpanda.runtime.preprocessor import preprocess_rpc

def run_rpc(code: str):
    """
    Run a .rpc script after preprocessing.
    """
    code = preprocess_rpc(code)

    # Global environment
    exec_globals = {'game': Game()}
    exec_globals['player'] = exec_globals['game'].player

    # Execute the code
    exec(code, exec_globals)
