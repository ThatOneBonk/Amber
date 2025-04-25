from io_handler import config_pull

def singleton(cls):
    """ Singleton boilerplate. """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class States:
    """ This class contains the temporary data storage used by various modules of this application. """
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._defaults = {
            "this_week_hash": "None",
            "next_week_hash": "None",
            "day_scope_start": "None",
            "day_scope_end": "None",
            "url_timetable": config_pull("url_timetable"),
            "url_groups": config_pull("url_groups")
        }
        self.__dict__.update(self._defaults)