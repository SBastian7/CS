import sys
from pathlib2 import Path # to work with Paths
import shutil # to work with files
import time 
import json # to work with json 
import zmq # to manage connection 

context = zmq.Context() 
socket = context.socket(zmq.REP)
socket.bind("tcp://*:6688") # Running on port 6688
print("Hello! I'm the server")
while True:
    #  Wait for next request from client
    message = socket.recv_multipart()
    resp = 0
    if message[0] == b'upload':
        file_info = {
            'file':message[1].decode('utf-8'),
            'owner':message[3].decode('utf-8'),
            'shr':""
        }
        path = Path('./files')
        folder = path / file_info['owner']
        fiile = path / file_info['owner'] / file_info['file']
        with open('users.txt') as json_file:
            data = json.load(json_file)
            if fiile.exists():
                print('Archivo Igual en Directorio')
                socket.send_multipart(['overwrite'])
                new_msg = socket.recv_string()
                if new_msg == 'Y' or new_msg == 'y':
                    file = open("files/"+file_info['owner']+"/"+message[1].decode('utf-8'),'wb')
                    file.write(message[2])
                    file.close()
                    with open('users.txt', 'w+') as outfile:
                        json.dump(data, outfile)
                    print('Operacion de sobrescritura exitosa')
                    socket.send_multipart(['Archivo Actualizado'])
                else:
                    print('Operacion de sobrescritura cancelada por el cliente')
                    socket.send_multipart(['Cancelado por usuario'])
            else:
                if not folder.is_dir():
                    print('Archivo agregado a nueva carpeta')
                    path = Path('./files/'+file_info['owner'])
                    path.mkdir(parents=True)
                else:
                    print('Archivo agregado a carpeta existente')
                file = open("files/"+file_info['owner']+"/"+message[1].decode('utf-8'),'wb')
                file.write(message[2])
                file.close()
                data.append(file_info)
                with open('users.txt', 'w+') as outfile:
                    json.dump(data, outfile)
                socket.send_multipart(['Archivo agregado'])
    if message[0] == b'download':
        user = message[3]
        target = message[2]
        path = Path('./files')
        folder = path / user
        fiile = path / user / target
        with open('users.txt') as json_file:
            data = json.load(json_file)
            if folder.is_dir():
                if fiile.exists():
                    file = open('files/'+user+'/'+target,'rb')
                    content = file.read()
                    resp = socket.send_multipart(['File Downloaded',target,content,user])
                    file.close()
                else:
                    resp = socket.send_multipart(['El archivo no existe en tu directorio'])
    if message[0] == b'share':
        user = message[3]
        target = message[2]
        items = ""
        path = Path('./files')
        folder = path / user
        fiile = path / user / target
        if folder.is_dir():
            with open('users.txt') as json_file:
                data = json.load(json_file)
                for files in data:
                    if files['owner'] == user:
                        if items == '':
                            items = files['file'].encode('utf-8')
                        else:
                            items = items+','+(files['file'].encode('utf-8'))
            socket.send_string(str(items))
            resp = socket.recv_multipart()
            items = items.split(',')
            print('*** ',len(items),'-',resp[0])
            if len(items) >= int(resp[0]) and int(resp[0]) != 0:
                print(str(items[int(resp[0])-1])+' para '+str(resp[1]))
                folder2 = path / str(resp[1])
                if not folder2.is_dir():
                    socket.send_string('El usuario destino no existe')    
                else:
                    with open('users.txt') as json_file:
                        data = json.load(json_file)
                        for i in data:
                            if i['file'] == str(items[int(resp[0])-1]):
                                if i['shr'] == "":
                                    i['shr'] = str(resp[1])
                                    data.append({'owner':str(resp[1]),'shr':'','file':str(items[int(resp[0])-1])})
                                    with open('users.txt', 'w+') as outfile:
                                        json.dump(data, outfile)
                                else:
                                    i['shr'] += ','+str(resp[1])
                                    data.append({'owner':str(resp[1]),'shr':'','file':str(items[int(resp[0])-1])})
                                    with open('users.txt', 'w+') as outfile:
                                        json.dump(data, outfile)
                                break
                        shutil.copy(str(folder)+'/'+str(items[int(resp[0])-1]), str(folder2))
                        socket.send_string('Archivo compartido exitosamente')
            else:
                socket.send_string('El indice seleccionado no existe en tu directorio.')
        else:
            socket.send_string('El usuario no existe')
    if message[0] == b'view':
        user = message[2]
        target = message[1]
        items = ""
        path = Path('./files')
        folder = path / user
        fiile = path / user / target
        if folder.is_dir():
            with open('users.txt') as json_file:
                data = json.load(json_file)
                for files in data:
                    if files['owner'] == user:
                        if items == '':
                            items = files['file'].encode('utf-8')
                        else:
                            items = items+','+(files['file'].encode('utf-8'))
            socket.send_string(str(items))
        else:
            socket.send_string('El usuario no existe')

