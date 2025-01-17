import paramiko
from base.INSTACE_PARAM import host, port, username, password, VERBOSE
from scp import SCPClient


class SSHCaller:
    
    def __init__(self):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.init_connection()


    def init_connection(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)
        except Exception as e:
            #print(e.__traceback__())
            raise(e)
        
        self.ssh = ssh

    def make_call_on_connection(self, command, filename, path, args, verbose):
        try:
            # Permite una ejecución por vía SSH en un servidor remoto
            scp = SCPClient(self.ssh.get_transport())
            scp.put(filename, f"{path}/" + filename)

            if verbose:
                print(command)

            stdin, stdout, stderr = self.ssh.exec_command(command)
            lines = stdout.readlines()

            # Elimina archivo creado en el servidor
            self.ssh.exec_command(f"rm {path}" + filename)

        except Exception as e:
            raise (e)
        
        return lines