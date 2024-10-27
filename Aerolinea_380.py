#Recursos Empleados para el funcionamiento del Programa
import pyodbc
import random
from faker import Faker
import datetime
import tkinter as tk
import tkinter as tkk
import threading
import tkinter.ttk as ttk
from tkinter import scrolledtext
#----------------------------------------------------------
fake = Faker('es_MX') 

# Conexión a la base de datos
def conectar_bd(database):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=DESKTOP-7E4SVP6;'
        f'DATABASE={database};'
        'UID=sa;' 
        'PWD=12345;'
    )
    return conn

# Funciones para obtener datos de la DB 'datos'

# Función para actualizar la barra de progreso
def actualizar_progreso(progress_bar, i, total):
    progreso = (i / total) * 100
    progress_bar['value'] = progreso
    root.update_idletasks()  # Esto actualiza la ventana mientras se ejecuta


def obtener_nombres(conn_datos):
    cursor = conn_datos.cursor()
    cursor.execute('SELECT nombre FROM nombres')
    nombres = cursor.fetchall()
    return [nombre[0] for nombre in nombres]  # Extraer los nombres en una lista

def obtener_apellidos(conn_datos):
    cursor = conn_datos.cursor()
    cursor.execute('SELECT apellido FROM apellidos')
    apellidos = cursor.fetchall()
    return [apellido[0] for apellido in apellidos]  # Extraer los apellidos en una lista

def obtener_estados(conn_datos):
    cursor = conn_datos.cursor()
    cursor.execute('SELECT cve_estado FROM estados')
    estados = cursor.fetchall()
    return [estado[0] for estado in estados]  # Extraer los estados en una lista

def obtener_municipios(conn_datos):
    cursor = conn_datos.cursor()
    cursor.execute('SELECT cve_municipios FROM municipios')
    municipios = cursor.fetchall()
    return [municipio[0] for municipio in municipios]  # Extraer los municipios en una lista

# Generar clientes con 100,000 registros
def generar_clientes():
    conn_airbus = conectar_bd("airbus380")
    conn_datos = conectar_bd("datos")
    total = 100000  
    
    cursor_airbus = conn_airbus.cursor()
    
    # Obtener los nombres, apellidos, estados y municipios de la base de datos "datos"
    nombres = obtener_nombres(conn_datos)
    apellidos = obtener_apellidos(conn_datos)
    estados = obtener_estados(conn_datos)
    municipios = obtener_municipios(conn_datos)
    
    for i in range(100000):
        # Seleccionar un nombre y dos apellidos aleatorios
        nombre = random.choice(nombres)
        paterno = random.choice(apellidos)
        materno = random.choice(apellidos)
        
        # Generar una fecha de nacimiento aleatoria con una edad entre 5 y 90 años
        edad = random.randint(5, 90)
        fecha_nacimiento = datetime.datetime.now() - datetime.timedelta(days=edad * 365)
        
        # Seleccionar claves de estado y municipio de manera aleatoria
        cve_estados = random.choice(estados)
        cve_municipios = random.choice(municipios)
        
        # Insertar el registro en la tabla clientes de airbus380
        cursor_airbus.execute(''' 
            INSERT INTO clientes (cve_municipios, cve_estados, nombre, paterno, materno, fecha_nacimiento)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cve_municipios, cve_estados, nombre, paterno, materno, fecha_nacimiento))

        # Actualizar barra de progreso
        actualizar_progreso(progress_bar_general, i + 1, total)
    
    conn_airbus.commit()
    historial_text.insert(tk.END, "DATOS Clientes CORRECTO.\n")
    
    conn_airbus.close()
    conn_datos.close()


# Generar registros para vuelos y sus detalles
def obtener_vuelos_mexico(conn_airbus):
    cursor = conn_airbus.cursor()
    
    # Consulta para obtener vuelos cuyo aeropuerto de origen o destino esté en México
    cursor.execute(''' 
        SELECT v.cve_vuelos 
        FROM vuelos v 
        JOIN aeropuertos a1 ON v.cve_aeropuertos__origen = a1.cve_aeropuertos 
        JOIN aeropuertos a2 ON v.cve_aeropuertos__destino = a2.cve_aeropuertos 
        JOIN paises p ON a1.cve_paises = p.cve_paises OR a2.cve_paises = p.cve_paises 
        WHERE p.nombre = 'México'
    ''')
    
    vuelos_mexico = cursor.fetchall()
    return [vuelo[0] for vuelo in vuelos_mexico]  # Extraer los cve_vuelos en una lista

def generar_detalle_vuelos():
    conn_airbus = conectar_bd("airbus380")
    cursor = conn_airbus.cursor()
    total = 10000
    
    # Obtener los vuelos que tienen aeropuertos en México
    vuelos_mexico = obtener_vuelos_mexico(conn_airbus)
    
    for i in range(10000):
        # Seleccionar un vuelo aleatorio de los vuelos en México
        cve_vuelo = random.choice(vuelos_mexico)
        
        # Generar una capacidad aleatoria entre 350 y 500 (solo múltiplos de 50)
        capacidad = random.choice([350, 400, 450, 500])
        
        # Generar una fecha y hora aleatoria en 2023, con hora en punto
        fecha_salida = datetime.datetime(
            year=2023, 
            month=random.randint(1, 12), 
            day=random.randint(1, 28),  # Usamos 28 para evitar días inválidos en meses como febrero
            hour=random.randint(0, 23)  # Cualquier hora en punto
        )
        
        # Insertar el registro en la tabla detalle_vuelos
        cursor.execute(''' 
            INSERT INTO detalle_vuelos (cve_vuelos, fecha_hora_salida, capacidad) 
            VALUES (?, ?, ?)
        ''', (cve_vuelo, fecha_salida, capacidad))

        actualizar_progreso(progress_bar_general, i + 1, total)
    
    
    conn_airbus.commit()
    historial_text.insert(tk.END, " DATOS Detalle de vuelos CORRECTO.\n")
    
    conn_airbus.close()


# Obtener datos de clientes y vuelos
def obtener_clientes(conn_airbus):
    cursor = conn_airbus.cursor()
    cursor.execute('SELECT cve_clientes FROM clientes')
    clientes = cursor.fetchall()
    return [cliente[0] for cliente in clientes]  # Extraer los cve_clientes en una lista

def obtener_vuelos_y_capacidades(conn_airbus):
    cursor = conn_airbus.cursor()
    cursor.execute('SELECT cve_detalle_vuelos, capacidad FROM detalle_vuelos')
    vuelos = cursor.fetchall()
    
    # Crear un diccionario con los vuelos y sus capacidades
    vuelos_capacidades = {vuelo[0]: {'capacidad': vuelo[1], 'ocupantes': 0} for vuelo in vuelos}
    return vuelos_capacidades

# Generar registros para la tabla ocupaciones (1,000,000 registros)
def generar_ocupaciones():
    conn_airbus = conectar_bd("airbus380")
    cursor = conn_airbus.cursor()
    
    # Obtener los clientes y los vuelos con sus capacidades
    clientes = obtener_clientes(conn_airbus)
    vuelos_capacidades = obtener_vuelos_y_capacidades(conn_airbus)
    total = 200000
    
    for i in range(200000):
        # Seleccionar un cliente aleatorio
        cve_cliente = random.choice(clientes)
        
        # Seleccionar un vuelo que aún tenga espacio disponible
        vuelo_seleccionado = None
        while vuelo_seleccionado is None:
            cve_vuelo = random.choice(list(vuelos_capacidades.keys()))
            if vuelos_capacidades[cve_vuelo]['ocupantes'] < vuelos_capacidades[cve_vuelo]['capacidad']:
                vuelo_seleccionado = cve_vuelo
                vuelos_capacidades[cve_vuelo]['ocupantes'] += 1  # Incrementar los ocupantes para ese vuelo
        
        # Insertar el registro en la tabla ocupaciones
        cursor.execute(''' 
            INSERT INTO ocupaciones (cve_detalle_vuelos, cve_clientes) 
            VALUES (?, ?)
        ''', (vuelo_seleccionado, cve_cliente))

        actualizar_progreso(progress_bar_general, i + 1, total)
    
    
    conn_airbus.commit()
    historial_text.insert(tk.END, "DATOS Ocupaciones CORRECTO .\n")
    
    conn_airbus.close()

# Función para eliminar todos los registros de una tabla
def eliminar_registros(tabla):
    conn_airbus = conectar_bd("airbus380")
    cursor = conn_airbus.cursor()
    
    # Ejecutar la consulta para eliminar todos los registros de la tabla seleccionada
    cursor.execute(f"DELETE FROM {tabla}")
    conn_airbus.commit()
    
    historial_text.insert(tk.END, f"Se han eliminado todos los registros de la tabla {tabla}.\n")
    
    conn_airbus.close()

#AREA DE INTERFAZ GRAFICA DE LA APLICACION----------------------------------------------------------------

# Crear la ventana principal
root = tk.Tk()
root.title("Aerolinea Airbus380-Lines")
root.geometry("800x550")  # Tamaño ajustado de la ventana
root.configure(bg="#F0F8FF")  # Fondo azul claro más suave

# Funciones para manejar los botones en hilos
def ejecutar_generar_clientes():
    thread = threading.Thread(target=generar_clientes)
    thread.start()

def ejecutar_generar_detalle_vuelos():
    thread = threading.Thread(target=generar_detalle_vuelos)
    thread.start()

def ejecutar_generar_ocupaciones():
    thread = threading.Thread(target=generar_ocupaciones)
    thread.start()

# Crear un marco principal para organizar los elementos
frame_principal = tk.Frame(root, bg="#F0F8FF")
frame_principal.pack(pady=20)

# Crear un título para la aplicación
titulo_label = tk.Label(frame_principal, text="Gestión de Datos de la Aerolínea", font=("Helvetica", 18, "bold"), bg="#F0F8FF", fg="#2F4F4F")
titulo_label.grid(row=0, columnspan=3, pady=10)

# Crear un marco para los botones
frame_botones = tk.Frame(frame_principal, bg="#F0F8FF")
frame_botones.grid(row=1, columnspan=3, pady=20)

# Lista de botones y sus respectivas funciones
botones = [
    ("Generar Datos Clientes", ejecutar_generar_clientes),
    ("Generar Datos Detalles de Vuelos", ejecutar_generar_detalle_vuelos),
    ("Generar Datos Ocupaciones", ejecutar_generar_ocupaciones),
    ("Limpiar Historial", lambda: historial_text.delete(1.0, tk.END)),
    ("Eliminar Registros", lambda: eliminar_registros(tabla_seleccionada.get()))
]

# Distribuir los botones en una cuadrícula, de 3 en 3
for i, (text, command) in enumerate(botones):
    row = i // 3
    col = i % 3
    button = ttk.Button(frame_botones, text=text, command=command, width=25)
    button.grid(row=row, column=col, padx=10, pady=5)

# Menú desplegable para seleccionar tabla
tablas_disponibles = ["clientes","clientes", "detalle_vuelos", "ocupaciones"]
tabla_seleccionada = tk.StringVar(root)
tabla_seleccionada.set(tablas_disponibles[0])  # Valor por defecto

menu_tablas = ttk.OptionMenu(frame_principal, tabla_seleccionada, *tablas_disponibles)
menu_tablas.grid(row=3, column=0, columnspan=3, pady=10)

# Crear una única barra de progreso
progress_bar_general = ttk.Progressbar(frame_principal, orient='horizontal', length=500, mode='determinate')
progress_bar_general.grid(row=4, columnspan=3, pady=10)

# Área de texto para mostrar el historial de ingresos
historial_text = scrolledtext.ScrolledText(frame_principal, width=50, height=50, bg="white", fg="black", bd=2, highlightbackground="#9370DB")
historial_text.grid(row=5, columnspan=3, pady=10)


#AREA DE INTERFAZ GRAFICA DE LA APLICACION----------------------------------------------------------------


root.mainloop()
