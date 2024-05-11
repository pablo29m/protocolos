import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_dir = ('localhost', 6667)
print('Conectando a %s puerto %s' % server_dir)
sock.connect(server_dir)

try:
    # Recibir mensaje de bienvenida del servidor
    print(sock.recv(1024).decode('utf-8'))

    while True:
        # Enviar mensaje al servidor
        mensaje = input("Mensaje para el servidor: ")
        sock.sendall(mensaje.encode('utf-8'))

        # Si el mensaje es "salir", cerrar la conexión y salir del bucle
        if mensaje.lower() == "salir":
            print("Cerrando conexión con el servidor...")
            break

        # Recibir respuesta del servidor
        try:
            data = sock.recv(1024)
            if not data:
                print("La conexión con el servidor se cerró.")
                break
            print(data.decode('utf-8'))
        except ConnectionResetError:
            print("La conexión con el servidor se cerró inesperadamente.")
            break

finally:
    print('Cerrando socket')
    sock.close()

