from enum import Enum


class ServerStreamEventType(str, Enum):
    ERROR = "error"
    EXECUTION_COMPLETE = "execution_complete"
    EXECUTION_COUNT = "execution_count"
    INIT = "init"
    PING = "ping"
    RESULT = "result"
    STATUS = "status"
    STDERR = "stderr"
    STDOUT = "stdout"

    def __str__(self) -> str:
        return str(self.value)
