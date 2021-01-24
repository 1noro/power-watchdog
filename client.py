#!/usr/bin/python

import sys, getopt, threading, requests, time, json
import os.path


config_file = 'config.json'
app_end = False
thread_pool = []

machine_name = None
ping_server = None
server_port = None
extra_servers = None


def load_config():
    global machine_name
    global ping_server
    global server_port
    global extra_servers
    if os.path.isfile(config_file):
        with open(config_file, 'r') as file:
            try:
                config_json = json.load(file)

                machine_name = config_json["default_name"]
                ping_server = config_json["default_server"]
                server_port = config_json["default_port"]
                extra_servers = config_json["extra_servers"]

            except ValueError:
                print("json parse of {} FAILED".format(config_file))


def pinger(name, server, port):
    while not app_end:
        url = "http://{}:{}/ping/{}".format(server, port, name)
        # response = requests.post(url = url)
        _ = requests.post(url = url)
        print("[ -> ]", url)
        # print("[ <- ]\n", response.text)
        time.sleep(20) # 20 segundos
    print("{} to {}:{} thread END".format(name, server, port))


def main(argv):
    global app_end
    global machine_name
    global ping_server
    global server_port

    load_config()

    help_str = 'client.py -n <machine_name> -s <ping_server> -p <server_port>'
    try:
        # opts, args = getopt.getopt(argv, "hn:s:", ["name=", "server="])
        opts, _ = getopt.getopt(argv, "hn:s:p:", ["name=", "server=", "port="])
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_str)
            sys.exit()
        elif opt in ("-n", "--name"):
            machine_name = arg
        elif opt in ("-s", "--server"):
            ping_server = arg
        elif opt in ("-p", "--port"):
            server_port = arg

    # print('machine_name:', machine_name)
    # print('ping_server:', ping_server)
    # print('server_port:', server_port)

    if machine_name is None or ping_server is None or server_port is None:
        print(help_str)
        sys.exit()
    else:
        thread_pool.append(threading.Thread(target=pinger, args=(machine_name, ping_server, server_port)))

    if extra_servers is not None:
        for info in extra_servers:
            if "name" in info and "server" in info and "port" in info:
                thread_pool.append(threading.Thread(target=pinger, args=(info["name"], info["server"], info["port"])))

    print('[info] write "quit" or press "Ctrl+C" for exit')

    for thread in thread_pool:
        thread.start()

    while True:
        try:
            command = input()
        except KeyboardInterrupt:
            command = 'quit'
        if command == 'quit':
            app_end = True
            break
    
    print('[info] waiting for all threads to end')

    for thread in thread_pool:
        thread.join()
    
    print('client END')


if __name__ == "__main__":
    main(sys.argv[1:])