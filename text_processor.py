from abc import ABC, abstractmethod


class TextProcessor(ABC):
    @abstractmethod
    def get_answer(self, client, messages, model):
        pass
