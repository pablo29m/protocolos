import socket
import select
import signal
import sys
from datetime import datetime

# Diccionario con los nombres de los meses en español
meses = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

# Lista para mantener las conexiones activas
conexiones_activas = []
sock = None
cerrando = False

def manejar_interrupcion(signal, frame):
    global cerrando
    print("\nSe ha detectado una interrupción. ¿Qué acción deseas tomar?")
    print("1. Cerrar solo el socket del servidor.")
    print("2. Cerrar todas las conexiones activas y luego cerrar el socket del servidor.")
    print("3. Salir sin cerrar nada.")

    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        cerrar_socket()
    elif opcion == "2":
        cerrar_conexiones()
        cerrar_socket()
        cerrando = True
        print("Saliendo del programa.")
        sys.exit(0)
    else:
        print("Saliendo sin cerrar nada.")
        sys.exit(0)

def cerrar_socket():
    global sock
    if sock:
        try:
            sock.close()
            print("Socket del servidor cerrado.")
            sys.exit(0)  # Salir del programa después de cerrar el socket del servidor
        except Exception as e:
            print("Error al cerrar el socket del servidor:", e)

def cerrar_conexiones():
    global conexiones_activas
    for conn in conexiones_activas:
        try:
            conn.close()
        except Exception as e:
            print("Error al cerrar conexión:", e)
    print("Todas las conexiones activas han sido cerradas.")

def proceso_hijo(conn, addr):
    global conexiones_activas, cerrando
    # Añadir la conexión activa a la lista
    conexiones_activas.append(conn)
    # Momento en que se establece la conexión
    inicio_conexion = datetime.now()

    print('Conexión establecida con IP: %s y Puerto: %s' % (addr[0], addr[1]))

    # Obtener la fecha y hora actual de conexión
    month_name = meses[inicio_conexion.month]  # Nombre del mes en español
    formatted_time = inicio_conexion.strftime("%H:%M")  # Formato de la hora
    friendly_date_time = f"{inicio_conexion.day} de {month_name} a las {formatted_time} hs"

    # Enviar el mensaje de bienvenida junto con la fecha y hora de conexión
    mensaje_bienvenida = f"Servidor: Conexión establecida el {friendly_date_time}. Puedes enviar mensajes al servidor.\n"
    conn.send(mensaje_bienvenida.encode('UTF-8'))

    while True:
        lista_para_leer, _, _ = select.select([conn], [], [], 0.1)
        for s in lista_para_leer:
            data = s.recv(1024).decode('utf-8')
            if not data:
                print('Cliente {}:{} se desconectó.'.format(addr[0], addr[1]))
                break
            if data.lower() == 'salir':
                print('Cliente {}:{} ha cerrado la conexión.'.format(addr[0], addr[1]))
                return  # Salir del bucle y terminar el proceso hijo

            if cerrando==False:
                print('Mensaje recibido de {}:{}: {}'.format(addr[0], addr[1], data))

            # Calcular la cantidad de tiempo transcurrido desde el inicio de la conexión
            tiempo_transcurrido = datetime.now() - inicio_conexion
            tiempo_transcurrido_formateado = str(tiempo_transcurrido)

            # Enviar el mensaje recibido junto con la cantidad de tiempo transcurrido
            mensaje_respuesta = f"Mensaje Recibido el {friendly_date_time}. Tiempo transcurrido desde la conexión: {tiempo_transcurrido_formateado}\n"
            try:
                conn.send(mensaje_respuesta.encode('UTF-8'))
            except OSError:
                break

    # Eliminar la conexión activa de la lista
    try:
        conexiones_activas.remove(conn)
    except ValueError:
        pass
    conn.close()

# servidor concurrente
host = "127.0.0.1"
port = 6667

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket creado")
sock.bind((host, port))
print("Enlace del socket completado")
sock.listen(5)
print("Socket en modo escucha")

# Manejar la señal de interrupción (Control+C)
signal.signal(signal.SIGINT, manejar_interrupcion)

while True:
    conn, addr = sock.accept()
    proceso_hijo(conn, addr)
