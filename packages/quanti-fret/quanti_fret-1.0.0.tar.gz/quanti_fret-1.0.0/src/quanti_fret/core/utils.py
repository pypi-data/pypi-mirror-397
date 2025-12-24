class Singleton(type):
    """ Singleton class.

    You can inherit this class to make your own class a singleton.
    """
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
