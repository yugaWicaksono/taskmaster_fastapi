import uvicorn
from src import server

if __name__ == "__main__":
    """
    The main entry of the app, import src module and run it
    """
    uvicorn.run(server.api, host="127.0.0.1", port=8000)
