from shutil import move
from tempfile import mkstemp

import os
import subprocess


class NginxError(Exception):
    pass


def stop_nginx_server(nginx_config_path):
    cmd = ["nginx", "-c", nginx_config_path, "-s", "stop"]
    subprocess.call(cmd, stderr=subprocess.DEVNULL)


def _start_nginx_server(nginx_config_path):
    cmd = ["nginx", "-c", nginx_config_path]
    if subprocess.call(cmd) != 0:
        raise NginxError("Failed to start nginx with congig " + nginx_config_path)


def _change_port_nginx_server(nginx_config_path, http_version):
    fh, tmp_path = mkstemp()
    new_port_number = -1
    with open(tmp_path, 'w') as new_file:
        with open(nginx_config_path) as old_file:
            for line in old_file:
                split_line = line.split()
                if len(split_line) >= 2 and split_line[0] == "listen":
                    old_port_number = int(split_line[1][:-1])
                    new_port_number = ((old_port_number - 32768) + 1) % 32768 + 32768
                    if str(http_version) == "2":
                        new_file.write(split_line[0] + " " + str(new_port_number) + " http2;\n")
                    else:
                        new_file.write(split_line[0] + " " + str(new_port_number) + ";\n")
                else:
                    new_file.write(line)

    os.close(fh)

    os.remove(nginx_config_path)
    move(tmp_path, nginx_config_path)
    return new_port_number


def launch_nginx_server(nginx_config_path, http_version):
    stop_nginx_server(nginx_config_path)
    port_number = _change_port_nginx_server(nginx_config_path, http_version)
    _start_nginx_server(nginx_config_path)
    return port_number
