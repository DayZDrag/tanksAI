from typing import Callable, Any

from tank import Tank

filter_tanks_name = lambda name: not [True for tank in Tank.tanks if tank.name == name]
filter_tanks_alive = lambda tanks: [True for tank in tanks if tank.is_alive]

def ocurat_print(SIZE_BORDER: object = 15, BORDER: object = "="):
    def decorator(func):

        def logic():
            print(BORDER*SIZE_BORDER)
            func()
            print(BORDER * SIZE_BORDER)

        return logic
    return decorator
