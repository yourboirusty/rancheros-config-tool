from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from ruamel.yaml.scalarstring import PreservedScalarString
import os

import http.server
import socketserver

MAIN_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

#Generated file name
GEN_FILE = 'built-cloud-config.yml'

#Default configuration
EXEC = ['sh', 'local', 'py', 'bash']
PERMS = {"exec":"0755", "other":"0644"}

#Network request serve settings
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = GEN_FILE
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

PORT = 8080
HANDLER = RequestHandler


#Yaml configuration
YML=YAML()

YML.indent(mapping=2, sequence=4, offset=2)
YML.encoding = "utf-8"
YML.allow_unicode=True


def get_config():
    with open(MAIN_DIR+'/config/cloud-config.yml','r') as sys_config_file:
        sys_config = sys_config_file.read()
    return YML.load(sys_config)


def write_keys(sys_yaml):
    if not 'ssh_publickeys' in sys_yaml:
        sys_yaml['ssh_publickeys']=list()
    try:
        with open(MAIN_DIR+'/config/pub_keys', 'r') as pub_key_file:
            for key in pub_key_file:
                sys_yaml['ssh_authorized_keys'].append(key.replace('\n',''))
    except OSError:
        print("No pub_keys file or can't read it, skipping")
    return sys_yaml


def build_file(path, file):
    with open(path+'/'+file, 'r') as data:
        content = data.read()
    try:
        perms=[line for line in content.split('\n') if "__perms__" in line]
        perms=perms[0].split(' ')[1]
    except IndexError:
        if file.split('.')[len(file.split('.'))-1] in EXEC:
            perms = PERMS['exec']
        else:
            perms = PERMS['other']
        print("Couldn't find perms in file "+file+", defaulting to " +perms)
    try:
        owner = [line for line in content.split('\n') if "__ownr__" in line]
        owner = owner[0].split(' ')[1]
    except IndexError:
        print("Couldn't find owner in file "+file+", defaulting to root")
        owner = "root"
    yaml = {"path": path.replace(MAIN_DIR+'/config/system/', '/')+'/'+file}
    yaml['permissions'] = perms
    yaml['owner'] = owner
    yaml['content'] = PreservedScalarString(content)
    return yaml


def write_files(sys_yaml):
    system_files = os.walk(MAIN_DIR+"/config/system/")
    if not 'write_files' in sys_yaml:
        sys_yaml['write_files'] = list()
    for root, dirs, files in system_files:
        for name in files:
            sys_yaml['write_files'].append(build_file(root.replace('\\', '/'), name))
    return sys_yaml


def serve_file():
    print("trying to create socket")
    with socketserver.TCPServer(("", PORT), HANDLER) as httpd:
        print("Serving file at port " + str(PORT))
        httpd.serve_forever()


def main():
    yaml_config = get_config()
    yaml_config = write_keys(yaml_config)
    yaml_config = write_files(yaml_config)

    with open(GEN_FILE,'w') as built:
        YML.dump(yaml_config, built)

    print("\n Do you want to serve the file?")
    print("Y/N")
    x = input()
    if(x.lower() == 'y'):
        serve_file()


if __name__ =="__main__":
    main()
