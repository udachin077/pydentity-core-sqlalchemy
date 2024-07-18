from pydentity.resources import Resources


class RoleNotFound(Exception):
    def __init__(self, name):
        super().__init__(Resources['RoleNotFound'].format(name))
