import json

class Conf:
    def __init__(self, confPath):
        try:
            with open(confPath) as f:
                conf = json.load(f)
            self.__dict__.update(conf)
        except Exception as e:
            print(f"Config Error: {e}")
            self.__dict__ = {}

    def __getitem__(self, k):
        return self.__dict__.get(k, None)