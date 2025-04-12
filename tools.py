from tank import Tank

filter_tanks_name = lambda name: not [True for tank in Tank.tanks if tank.name == name]
filter_tanks_alive = lambda tanks: [True for tank in tanks if tank.is_alive]