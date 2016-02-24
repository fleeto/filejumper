import json
import os
import glob
import uuid
import jumper.host
import datetime
import hashlib

class Task:
    def __init__(self, config_path, host):
        self.id = ""
        self.file = ""
        self.status = ""
        self.position = ""
        self.task_file = ""
        self.host = host
        self.status = ""
        self.log = []
        self.config_path = config_path
        self.path = os.path.join(config_path, 'task')

    def load_by_id(self, task_id):
        task_file_list = glob.glob(os.path.join(self.path, "*.json"))
        for task_file in task_file_list:
            try:
                handler = open(task_file, "r")
                task_obj = json.load(handler)
            except Exception as e:
                print "Parsing task_file '%s' failed." % task_file
                print e.message
                continue
            finally:
                handler.close()
            if ("id" in task_obj.keys()) and (task_obj["id"] == task_id):
                self.task_file = task_file
                self._from_json(task_obj)
                break

    def load_by_file(self, file_name):
        handler = open(file_name, "r")
        task_obj = json.load(handler)
        if task_obj["file"] == file_name:
            self.task_file = file_name
            self._from_json(task_obj)

    def find_task_by_status(self, status):
        task_list = []
        task_file_list = glob.glob(os.path.join(self.path, "*.json"))
        for task_file in task_file_list:

            try:
                handler = open(task_file, "r")
                task_obj = json.load(handler)
            except Exception as e:
                print "Parsing task_file '%s' failed." % task_file
                print e.message
                continue
            finally:
                handler.close()

            if task_obj["status"] in ["failed", "finished"]:
                continue

            if status == "new":
                if task_obj["id"] == "" or task_obj["position"] == "" or task_obj["position"] == self.host:
                    new_task = Task(self.config_path, self.host)
                    new_task.load_by_id(task_obj["id"])
                    task_list.append(new_task)
            if status == "running" and task_obj["status"] == "running":
                new_task = Task(self.config_path, self.host)
                new_task.load_by_id(task_obj["id"])
                task_list.append(new_task)
        return task_list

    def _from_json(self, json_obj):
        self.file = json_obj["file"]
        self.task_id = json_obj["id"]
        self.position = json_obj["position"]
        self.target = json_obj["target"]
        self.status = json_obj["status"]
        if "log" in json_obj.keys():
            self.log = json_obj["log"]

    def save(self):
        handler = open(self.task_file, "w")
        if len(self.task_id) == 0:
            self.task_id = uuid.uuid1().hex

        task_obj = {"id": self.task_id, "file": self.file, "target": self.target,
                    "position": self.position, "status": self.status, "log": self.log}
        json.dump(task_obj, handler, indent=2)
        handler.close()

    def execute(self):
        host_config_obj = jumper.host.Host(self.config_path, self.host)
        send_to = host_config_obj.find_next(self.target)
        print "Processing task: %s" % self.task_file
        result = True
        try:
            print "Target host: %s" % send_to.host_id
            real_file = os.path.join(self.config_path, "data", self.file)
            print "Sending %s" % real_file
            # upload data file
            Task._upload_file(real_file, send_to, "data")

            self.position = send_to.host_id
            if self.position == self.target:
                self.status = "finished"
            else:
                self.status = "running"

            # Append the action log
            log_record = {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          "host": self.host,
                          "hash": Task._file_hash(os.path.join(self.config_path, 'data', self.file))}
            self.log.append(log_record)

            self.save()

            # upload task file
            print "Sending Task File %s" % self.task_file
            Task._upload_file(self.task_file, send_to, "task")


        except Exception as e:
            print e.message
            result = False
        # log_record = {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #               "host": self.host, "hash": Task._file_hash(self.file)}
        # self.log.append(log_record)
        self.save()
        # Update status
        if not result:
            self.status = "failed"
            self.save()

    @staticmethod
    def _file_hash(file_name):
        block_size = 65536
        hash_tool = hashlib.md5()
        with open(file_name, 'rb') as afile:
            buf = afile.read(block_size)
            while len(buf) > 0:
                hash_tool.update(buf)
                buf = afile.read(block_size)
        return hash_tool.hexdigest()

    def write_log(self, action, to_host, result):
        log_name, ext_name = os.path.splitext(os.path.basename(self.task_file))
        log_file = os.path.join(self.config_path, 'result', log_name + '.log')
        if os.path.exists(log_file):
            handler = open(log_file, 'a')
        else:
            handler = open(log_file, "w")

        # date time, file hash, action, from host\t, to host\t, result,file_name
        dt = datetime.datetime.now()
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        file_hash = Task._file_hash(os.path.join(self.config_path, 'data', self.file))
        from_host = self.host
        file_name = self.file
        content = "%s,%s,%s,%s\t,%s\t,%s\t,%s\r\n" % (
            dt_str, file_hash, action, from_host, to_host.host_id, result, file_name)
        handler.write(content)
        handler.close()

    @staticmethod
    def _upload_file(source, host, additional):
        command = "sshpass -p '%s' scp -P %s %s %s@%s:%s" % \
                  (host.password, host.port, source, host.user,
                   host.host, os.path.join(host.path, additional))
        return os.system(command)

    # update task info from next step
    def update_task(self):
        host_config_obj = jumper.host.Host(self.config_path, self.host)
        target = host_config_obj.find_next(self.target)
        command = "sshpass -p '%s' scp -P %s %s@%s:%s %s" % \
                  (target.password, target.port, target.user, target.host,
                   os.path.join(target.config_path, 'task',os.path.basename(self.task_file)),
                   self.task_file
                   )
        return os.system(command)



