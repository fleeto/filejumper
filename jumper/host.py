import json
import os


class Host:
    def __init__(self, config_path, host=""):
        self.host_id = ""
        self.config = os.path.join(config_path, "host.json")
        self.config_path = config_path
        self.load_by_id(host)

    def find_next(self, target):
        file_opr = open(self.config, "r")
        host_list_obj = json.load(file_opr)
        last_host = target
        while True:
            host_obj = host_list_obj[last_host]
            upstream = host_obj['upstream']
            if (upstream == self.host_id) or (upstream == ""):
                return Host(self.config_path, last_host)
            else:
                last_host = upstream
        return None

    def load_by_id(self, host_id):
        file_opr = open(self.config, "r")
        self.host_id = host_id
        host_list_obj = json.load(file_opr)
        self._from_json(host_id, host_list_obj[host_id])

    def _from_json(self, host_id, json_obj):
        self.host_id = host_id
        self.host = json_obj['host']
        self.port = json_obj['port']
        self.user = json_obj['user']
        self.password = json_obj['pass']
        self.path = json_obj['path']

    def clean(self):
        self.host_id = ""
