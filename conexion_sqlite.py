import sqlite3

class Comunicacion():
    def __init__(self) -> None:
        try:
            self.conexion = sqlite3.connect('BD_medicamentos.db')
            self.crear_tabla_si_no_existe()
        except sqlite3.Error as e:
            print("Error al conectar a la base de datos:", e)

    def crear_tabla_si_no_existe(self):
        try:
            cursor = self.conexion.cursor()
            bd = '''
            CREATE TABLE IF NOT EXISTS tabla_datos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CODIGO TEXT NOT NULL UNIQUE,
                NOMBRE TEXT NOT NULL,
                VENCIMIENTO TEXT NOT NULL
            )
            '''
            cursor.execute(bd)
            self.conexion.commit()
            cursor.close()
        except sqlite3.Error as e:
            print("Error al crear la tabla:", e)

    def insertar_productos(self, codigo, nombre, vencimiento):
        try:
            cursor = self.conexion.cursor()
            bd = '''INSERT INTO tabla_datos (CODIGO, NOMBRE, VENCIMIENTO)
            VALUES ("{}","{}", "{}");'''.format(codigo, nombre, vencimiento)
            cursor.execute(bd)
            self.conexion.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print("Error al insertar productos:", e)
            return False

    def mostrar_productos(self):
        try:
            cursor = self.conexion.cursor()
            bd = "SELECT * FROM tabla_datos"
            cursor.execute(bd)
            registro = cursor.fetchall()
            return registro
        except sqlite3.Error as e:
            print("Error al mostrar productos:", e)
            return []

    def buscar_productos(self, codigo):
        try:
            cursor = self.conexion.cursor()
            bd = '''SELECT * FROM tabla_datos WHERE CODIGO = ?'''
            cursor.execute(bd, (codigo,))
            resultado = cursor.fetchall()
            cursor.close()
            return resultado
        except sqlite3.Error as e:
            print("Error al buscar productos:", e)
            return []

    def eliminar_productos_por_codigo(self, codigo):
        try:
            cursor = self.conexion.cursor()
            bd = '''DELETE FROM tabla_datos WHERE CODIGO = ?'''
            cursor.execute(bd, (codigo,))
            self.conexion.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print("Error al eliminar productos:", e)
            return False

    def actualizar_productos(self, Id, codigo, nombre, vencimiento):
        try:
            cursor = self.conexion.cursor()

            # Obtener el código actual del producto
            codigo_actual = self.obtener_codigo_producto_por_id(Id)

            if codigo != codigo_actual and self.verificar_codigo_existente(codigo):
                print("Error: El código ya existe en la base de datos.")
                return 0

            bd = '''UPDATE tabla_datos SET CODIGO='{}', NOMBRE='{}', VENCIMIENTO= '{}'
            WHERE ID = '{}' '''.format(codigo, nombre, vencimiento, Id)
            cursor.execute(bd)
            a = cursor.rowcount
            self.conexion.commit()
            cursor.close()
            return a
        except sqlite3.Error as e:
            print("Error al actualizar productos:", e)
            return -1

    def verificar_codigo_existente(self, codigo):
        try:
            cursor = self.conexion.cursor()
            query = "SELECT COUNT(*) FROM tabla_datos WHERE CODIGO = ?"
            cursor.execute(query, (codigo,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count > 0
        except sqlite3.Error as e:
            print("Error al verificar código existente:", e)
            return False
    
    def obtener_codigo_producto_por_id(self, Id):
        try:
            cursor = self.conexion.cursor()
            bd = '''SELECT CODIGO FROM tabla_datos WHERE ID = ?'''
            cursor.execute(bd, (Id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            if resultado:
                return resultado[0]
            else:
                return None
        except sqlite3.Error as e:
            print("Error al obtener el código del producto por ID:", e)
            return None


    def cerrar_conexion(self):
        try:
            self.conexion.close()
        except sqlite3.Error as e:
            print("Error al cerrar la conexión:", e)
