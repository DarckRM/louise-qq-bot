from typing import Callable

from botpy.message import DirectMessage


def on_command(cmd: str):
    def decorator(invoke: Callable):
        async def wrapper(*args):
            message: DirectMessage = args[1]
            if message.content.startswith(cmd):
                if await invoke(message):
                    return 0
                else:
                    return 1
            else:
                return -1
        return wrapper
    return decorator