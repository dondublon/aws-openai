from abc import ABC, abstractmethod
class ChatStore(ABC):
    @abstractmethod
    def create_session(name:str = None)->str:
        pass
    @abstractmethod
    def get_messages(session_id: str)-> list[dict]:
        pass
    @abstractmethod
    def append_message(session_id: str, role: str, content: str):
        pass