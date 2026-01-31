from typing import Callable, Any

#from tank import Tank
import inspect

filter_tanks_name = lambda name, tanks: not [True for tank in tanks if tank.name == name]
filter_tanks_alive = lambda tanks: [True for tank in tanks if tank.is_alive]

def ocurat_print(SIZE_BORDER: object = 15, BORDER: object = "="):
    def decorator(func):

        def logic():
            print(BORDER*SIZE_BORDER)
            func()
            print(BORDER * SIZE_BORDER)

        return logic
    return decorator

def log(msg):

    frame = inspect.currentframe().f_back or inspect.currentframe()
    file = inspect.getfile(frame)
    line = frame.f_lineno


    for name, val in list(frame.f_locals.items()):
        if val is msg:
            break

    print(f"[{file}:{line}] {name}={msg}")