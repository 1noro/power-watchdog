import json
import threading
import time
from datetime import datetime
import os.path
from flask import Flask, request  # python-flask

app = Flask(__name__)
db_file = __file__.replace(".py", "") + "_db.json"


@app.route('/', methods=["GET"])
def index():
    data = None
    out = "<pre>\n"
    with open(db_file, 'r') as file:
        data = json.load(file)
    for name in data.keys():
        status_str = " OK "
        if not data[name]["active"]:
            status_str = "FAIL"
        out += "[{}]\t{}\t({})\n".format(status_str, data[name]["ip"], name)
    return out + "</pre>", 200


@app.route('/health-check', methods=["GET"])
def health_check():
    return "Ok", 200


@app.route('/ping/<name>', methods=["POST"])
def ping(name):
    data = None
    with open(db_file, 'r') as file:
        data = json.load(file)
    with open(db_file, 'w') as file:
        if name not in data:
            data[name] = {}
        data[name]["ip"] = request.remote_addr
        data[name]["timestamp"] = datetime.timestamp(datetime.now())
        data[name]["active"] = True
        json.dump(data, file)
    return "pong", 201


@app.route("/ip", methods=["GET"])
def ip():
    return request.remote_addr, 200


def date_checker():
    while True:
        data = None
        names_to_pop = []
        with open(db_file, 'r') as file:
            data = json.load(file)
        for name in data.keys():
            if data[name]["active"]:
                old_date = datetime.fromtimestamp(data[name]["timestamp"])
                difference_min = (datetime.now() - old_date).total_seconds() / 60
                # print('?:', difference_min, '>', 1, name)
                if difference_min > 10080: # una semana
                    print("[----]\t{}\t({})".format(data[name]["ip"], name))
                    names_to_pop.append(name)
                elif difference_min > 3:
                    print("[FAIL]\t{}\t({})".format(data[name]["ip"], name))
                    data[name]["active"] = False
        for name in names_to_pop:
            data.pop(name, None)
        with open(db_file, 'w') as file:
            json.dump(data, file)
        time.sleep(20)


if __name__ == '__main__':
    if not os.path.exists(db_file):
        with open(db_file, 'w') as file:
            file.write("{}")

    check = threading.Thread(target=date_checker, args=())
    check.start()

    app.run(host='0.0.0.0')
