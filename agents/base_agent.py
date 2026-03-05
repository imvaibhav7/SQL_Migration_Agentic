from core.logger import log_agent_io


class BaseAgent:

    def __init__(self, llm):
        self.llm = llm
        self.name = self.__class__.__name__

    def _log_input(self, payload):
        log_agent_io(self.name, "input", payload)

    def _log_output(self, payload):
        log_agent_io(self.name, "output", payload)

    def run(self, payload):
        raise NotImplementedError

