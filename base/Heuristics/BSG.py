from random import randint
from base.INSTACE_PARAM import LOCAL_EXECUTION
from scp import SCPClient
from json.decoder import JSONDecodeError
import os
import sys
import subprocess
import json


class BSG():

    BSG_PATH = '.' if LOCAL_EXECUTION else '/home/iaraya/clp'
    remove_instance = True
    index_results = -2

    def bsg_solve(self,
                  boxes, bsg_time=1, args=""
                  ):

        persistens = True
        
        
        filename = "tmp_instance_" + str(randint(10000, 99999))
        self.write_instance(self.L, self.W, self.H, boxes, filename)

        loaded = {}
        remaining = {}

        # Permite una ejecución local del BSG_CLP
        if LOCAL_EXECUTION:
            index_results = -2
            command = [f'{self.BSG_PATH}/BSG_CLP', f'{self.BSG_PATH}/{filename}',
                       '-i', '0', '-t', f'{bsg_time}', '--json']

            args = args.split(" ")

            if len(args) > 0:
                command.extend(args)

            if self.verbose:
                print(command)

            # Persistencia en la conexion
            while persistens:
                try:
                    lines = subprocess.run(
                        command, capture_output=True, text=True).stdout.split('\n')
                    persistens = False
                except Exception as e:
                    print(e)
                    persistens = True
        else:

            index_results = -1
            # Permite una ejecución por vía SSH en un servidor remoto
            scp = SCPClient(self.ssh.get_transport())
            scp.put(filename, f"{self.BSG_PATH}/" + filename)

            command = f"{
                self.BSG_PATH}/BSG_CLP {self.BSG_PATH}/{filename} -i 0 -t {bsg_time} --json {args}"

            if self.verbose:
                print(command)

            # Persistencia en la conexion
            while persistens:
                try:
                    stdin, stdout, stderr = self.ssh.exec_command(command)
                    lines = stdout.readlines()
                    persistens = False
                except Exception as e:
                    print(e)
                    persistens = True

            # Elimina archivo creado en el servidor
            self.ssh.exec_command(f"rm {self.BSG_PATH}" + filename)
        # Se obtiene el resultado de la ejecución
        try:
            json_data = json.loads(lines[index_results])
        except (JSONDecodeError, IndexError) as e:
            print(lines)
            raise (e)

        for item in json_data["loaded"]:
            loaded[self.id2box[item[0]]] = item[1]
        for item in json_data["remaining"]:
            remaining[self.id2box[item[0]]] = item[1]

        if self.remove_instance:
            os.remove(filename)

        return (
            remaining,
            loaded,
            json_data,
        )

    def write_instance(self, L, W, H, boxes, filename):
        txt = f"1\n1 0\n{L} {W} {H}\n"
        txt += str(len(boxes)) + "\n"
        for it_box in boxes:
            txt += f"{it_box.id} {it_box.l} {it_box.rotx} {it_box.w} {
                it_box.roty} {it_box.h} {it_box.rotz} {boxes[it_box]}\n"
        txt += "\n"

        text_file = open(filename, "w")
        text_file.write(txt)
        text_file.close()
