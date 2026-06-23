
import json


class CommonLogger:

    def __init__(self, filepath):
        self.file = open(filepath, "a")

    def log(self, record):
        self.file.write(
            json.dumps(record) + "\n"
        )

    def close(self):
        self.file.close()