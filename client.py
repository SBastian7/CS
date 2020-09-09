# CLIENTFILES
import zmq
import sys
import json

# Context
context = zmq.Context()

# Sockets
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:6688")

# Option
op = sys.argv[1]

if op == 'upload':
    names = input("Ingresa tu nombre: ")
    url = sys.argv[2]
    file = open(url,'rb')
    content = file.read()
    socket.send_multipart([b'upload',url.encode('utf-8'),content,names])
    resp = socket.recv_multipart()
    if resp[0] == 'overwrite':
        opt = input('Deseas sobrescribir el archivo? (Y/N): ')
        socket.send_string(opt)
        resp2 = socket.recv_multipart();
        print('Response: ',resp2[0])
    else:
        print('Response: ',resp)
    file.close()

elif op == 'download':
    names = input("Ingresa tu nombre: ")
    url = sys.argv[2]
    socket.send_multipart([b'download','list',url,names])
    message = socket.recv_multipart()
    if message[0] == 'File Downloaded':
        file = open(message[1].decode('utf-8'),'wb')
        file.write(message[2])
        file.close()
    print("Response: "+str(message[0]))

elif op == 'share':
    names = input("Ingresa tu nombre: ")
    url = sys.argv[2]
    socket.send_multipart([b'share',url.encode('utf-8'),url.encode('utf-8'),names.encode('utf-8')])
    response = socket.recv_string()
    if response != 'El usuario no existe':
        response = response.split(',')
        print('\nTus archivos:\n')
        for idx,item in enumerate(response):
            print(str(idx+1)+'. '+item.decode('utf-8'))
        opt = input('\nIngresa el numero del archivo que deseas compartir: ')
        usr = input('Ingresa el nombre del usuario al que lo quieres compartir: ')
        resp = socket.send_multipart([str(opt).encode('utf-8'),usr.encode('utf-8')])
        print(socket.recv_string())
    else:
        print("Response: "+response)

elif op == 'view':
    url = sys.argv[2]
    names = input("Ingresa tu nombre: ")
    socket.send_multipart([b'view',url.encode('utf-8'),names.encode('utf-8')])
    response = socket.recv_string()
    if response != 'El usuario no existe':
        response = response.split(',')
        print('\nTus archivos:\n')
        for idx,item in enumerate(response):
            print(str(idx+1)+'. '+item.decode('utf-8'))
        print('\n')
else:
    resp= socket.recv_multipart()
    print(str(resp))
