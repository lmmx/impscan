__all__ = ["EnvConfig"]


class EnvConfig:
    def __init__(self, **kwargs):
        self.settings = set()
        for k, v in kwargs.items():
            self.set_config(k, v)

    def set_config(self, setting, value):
        setattr(self, setting, value)
        self.settings.add(setting)
