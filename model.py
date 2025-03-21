import mysql.connector
import pandas as pd
import datetime

class Database:
    def __init__(self):
        self.connection_params = {
            "host": "bgdga4cscenfj5utxtiy-mysql.services.clever-cloud.com",
            "port": 3306,
            "user": 'ufylrms2atfe3d7t',
            "password": "kv1WXEaHPezZz0KtnKqa",
            "database": "bgdga4cscenfj5utxtiy"
        }
    
    def get_db_connection(self):
        """Obtiene una conexión a la base de datos"""
        return mysql.connector.connect(**self.connection_params)

    def obtener_tipos_usuarios(self):
        """Obtiene un diccionario de tipos de usuarios {id: nombre}"""
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        tipos_usuarios = {}
        
        try:
            cursor.execute("SELECT id_tipo_usuario, nombre_tipo_usuario FROM tipos_usuarios")
            for row in cursor.fetchall():
                tipos_usuarios[row['id_tipo_usuario']] = row['nombre_tipo_usuario']
            return tipos_usuarios
        except Exception as e:
            raise Exception(f"Error al obtener tipos de usuarios: {e}")
        finally:
            cursor.close()
            conn.close()
            
    def obtener_tipos_vehiculos(self):
        """Obtiene un diccionario de tipos de vehículos {id: nombre}"""
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        tipos_vehiculos = {}
        
        try:
            cursor.execute("SELECT id_tipo_vehiculo, nombre_tipo_vehiculo FROM tipos_vehiculos")
            for row in cursor.fetchall():
                tipos_vehiculos[row['id_tipo_vehiculo']] = row['nombre_tipo_vehiculo']
            return tipos_vehiculos
        except Exception as e:
            raise Exception(f"Error al obtener tipos de vehículos: {e}")
        finally:
            cursor.close()
            conn.close()

    def obtener_parqueo(self):
        """Obtiene información de todos los espacios de parqueo"""
        try:
            conn = self.get_db_connection()
            query = """
                SELECT ep.id_espacio_parqueo, ep.id_estado, ep.id_seccion, 
                       e.nombre_estado, sp.nombre_seccion
                FROM espacios_parqueo ep
                JOIN estados e ON ep.id_estado = e.id_estado
                JOIN secciones_parqueos sp ON ep.id_seccion = sp.id_seccion
            """
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            raise Exception(f"Error al obtener datos del parqueo: {e}")

    def obtener_usuario_por_codigo(self, codigo_universitario):
        """Obtiene información de un usuario por su código universitario"""
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = """
                SELECT u.id_usuario, u.codigo_universitario, u.nombre_usuario, 
                       u.id_tipo_usuario, tu.nombre_tipo_usuario
                FROM usuarios u
                JOIN tipos_usuarios tu ON u.id_tipo_usuario = tu.id_tipo_usuario
                WHERE u.codigo_universitario = %s
            """
            cursor.execute(query, (codigo_universitario,))
            usuario = cursor.fetchone()
            return usuario
        except Exception as e:
            raise Exception(f"Error al obtener usuario: {e}")
        finally:
            cursor.close()
            conn.close()
            
    def obtener_vehiculo_por_usuario(self, id_usuario):
    #Obtiene información del vehículo asociado a un usuario
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT v.id_sticker, v.placa, v.id_tipo_vehiculo, v.id_color, 
                        v.id_modelo, v.id_marca, tv.nombre_tipo_vehiculo,
                        m.nombre_marca, mo.nombre_modelo, c.nombre_color
                FROM vehiculos v
                JOIN tipos_vehiculos tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
                JOIN marcas m ON v.id_marca = m.id_marca
                JOIN modelos mo ON v.id_modelo = mo.id_modelo
                JOIN colores c ON v.id_color = c.id_color
                WHERE v.id_usuario = %s
            """
            cursor.execute(query, (id_usuario,))
            vehiculo = cursor.fetchone()  # Leer el resultado de la consulta
            return vehiculo
        except Exception as e:
            raise Exception(f"Error al obtener vehículo: {e}")
        finally:
            cursor.close()  # Ahora el cursor se cierra correctamente
            conn.close()  # Ahora la conexión se cierra correctamente   

    def agregar_usuario(self, codigo_universitario, nombre_usuario, email_contacto, 
                      telefono_contacto, id_tipo_usuario, placa, 
                      id_tipo_vehiculo, nombre_marca, nombre_modelo, nombre_color):
        """Agrega un nuevo usuario con su vehículo al sistema"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id_usuario FROM usuarios WHERE codigo_universitario = %s", 
                          (codigo_universitario,))
            if cursor.fetchone():
                raise Exception("El código universitario ya está registrado")
                
            # Verificar si la placa ya existe
            cursor.execute("SELECT id_sticker FROM vehiculos WHERE placa = %s", (placa,))
            if cursor.fetchone():
                raise Exception("La placa ya está registrada en el sistema")
            
            # 1. Insertar contacto
            cursor.execute(
                "INSERT INTO contactos (email_contacto, telefono_contacto) VALUES (%s, %s)", 
                (email_contacto, telefono_contacto)
            )
            id_contacto = cursor.lastrowid
            
            # 2. Insertar usuario
            cursor.execute(
                "INSERT INTO usuarios (codigo_universitario, nombre_usuario, id_contacto, id_tipo_usuario) VALUES (%s, %s, %s, %s)", 
                (codigo_universitario, nombre_usuario, id_contacto, id_tipo_usuario)
            )
            id_usuario = cursor.lastrowid
            
            # 3. Procesar datos del vehículo
            
            # 3.1 Marca
            cursor.execute("SELECT id_marca FROM marcas WHERE nombre_marca = %s", (nombre_marca,))
            marca = cursor.fetchone()
            if marca:
                id_marca = marca[0]
            else:
                cursor.execute("INSERT INTO marcas (nombre_marca) VALUES (%s)", (nombre_marca,))
                id_marca = cursor.lastrowid
            
            # 3.2 Modelo
            cursor.execute("SELECT id_modelo FROM modelos WHERE nombre_modelo = %s", (nombre_modelo,))
            modelo = cursor.fetchone()
            if modelo:
                id_modelo = modelo[0]
            else:
                cursor.execute("INSERT INTO modelos (nombre_modelo) VALUES (%s)", (nombre_modelo,))
                id_modelo = cursor.lastrowid
            
            # 3.3 Color
            cursor.execute("SELECT id_color FROM colores WHERE nombre_color = %s", (nombre_color,))
            color = cursor.fetchone()
            if color:
                id_color = color[0]
            else:
                cursor.execute("INSERT INTO colores (nombre_color) VALUES (%s)", (nombre_color,))
                id_color = cursor.lastrowid
            
            # 4. Insertar vehículo
            cursor.execute(
                "INSERT INTO vehiculos (placa, id_tipo_vehiculo, id_color, id_modelo, id_marca, id_usuario) VALUES (%s, %s, %s, %s, %s, %s)", 
                (placa, id_tipo_vehiculo, id_color, id_modelo, id_marca, id_usuario)
            )
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al agregar usuario: {e}")
        finally:
            cursor.close()
            conn.close()
            
    def actualizar_vehiculo(self, id_usuario, placa, id_tipo_vehiculo, nombre_marca, nombre_modelo, nombre_color):
        """Actualiza la información del vehículo de un usuario"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar que la placa no esté en uso por otro vehículo
            cursor.execute(
                "SELECT id_sticker FROM vehiculos WHERE placa = %s AND id_usuario != %s", 
                (placa, id_usuario)
            )
            if cursor.fetchone():
                raise Exception("La placa ya está registrada por otro usuario")
            
            # Procesar datos del vehículo
            
            # Marca
            cursor.execute("SELECT id_marca FROM marcas WHERE nombre_marca = %s", (nombre_marca,))
            marca = cursor.fetchone()
            if marca:
                id_marca = marca[0]
            else:
                cursor.execute("INSERT INTO marcas (nombre_marca) VALUES (%s)", (nombre_marca,))
                id_marca = cursor.lastrowid
            
            # Modelo
            cursor.execute("SELECT id_modelo FROM modelos WHERE nombre_modelo = %s", (nombre_modelo,))
            modelo = cursor.fetchone()
            if modelo:
                id_modelo = modelo[0]
            else:
                cursor.execute("INSERT INTO modelos (nombre_modelo) VALUES (%s)", (nombre_modelo,))
                id_modelo = cursor.lastrowid
            
            # Color
            cursor.execute("SELECT id_color FROM colores WHERE nombre_color = %s", (nombre_color,))
            color = cursor.fetchone()
            if color:
                id_color = color[0]
            else:
                cursor.execute("INSERT INTO colores (nombre_color) VALUES (%s)", (nombre_color,))
                id_color = cursor.lastrowid
            
            # Actualizar vehículo
            cursor.execute(
                """
                UPDATE vehiculos
                SET placa = %s, id_tipo_vehiculo = %s, id_color = %s, id_modelo = %s, id_marca = %s
                WHERE id_usuario = %s
                """, 
                (placa, id_tipo_vehiculo, id_color, id_modelo, id_marca, id_usuario)
            )
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar vehículo: {e}")
        finally:
            cursor.close()
            conn.close()

    def verificar_vehiculo_en_parqueo(self, id_sticker):
        """Verifica si un vehículo está actualmente en el parqueo"""
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = """
                SELECT vep.id_espacio_parqueo, vep.fecha_hora_ingreso
                FROM vehiculos_espacio_parqueo vep
                WHERE vep.id_sticker = %s AND vep.fecha_hora_salida IS NULL
                ORDER BY vep.fecha_hora_ingreso DESC
                LIMIT 1
            """
            cursor.execute(query, (id_sticker,))
            return cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al verificar vehículo en parqueo: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def registrar_ingreso(self, id_sticker, id_espacio_parqueo):
        """Registra el ingreso de un vehículo al parqueo"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar que el espacio esté disponible
            cursor.execute(
                "SELECT id_estado FROM espacios_parqueo WHERE id_espacio_parqueo = %s", 
                (id_espacio_parqueo,)
            )
            estado = cursor.fetchone()
            if not estado or estado[0] != 1:  # 1 = libre
                raise Exception("El espacio seleccionado no está disponible")
            
            # Registrar ingreso
            cursor.execute(
                """
                INSERT INTO vehiculos_espacio_parqueo 
                (id_espacio_parqueo, fecha_hora_ingreso, id_sticker)
                VALUES (%s, %s, %s)
                """, 
                (id_espacio_parqueo, datetime.datetime.now(), id_sticker)
            )
            
            # Actualizar estado del espacio a ocupado
            cursor.execute(
                "UPDATE espacios_parqueo SET id_estado = 2 WHERE id_espacio_parqueo = %s",  # 2 = ocupado
                (id_espacio_parqueo,)
            )
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al registrar ingreso: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def registrar_salida(self, id_sticker):
        """Registra la salida de un vehículo del parqueo"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar el registro de ingreso más reciente sin salida
            cursor.execute(
                """
                SELECT id_espacio_parqueo, fecha_hora_ingreso
                FROM vehiculos_espacio_parqueo
                WHERE id_sticker = %s AND fecha_hora_salida IS NULL
                ORDER BY fecha_hora_ingreso DESC
                LIMIT 1
                """, 
                (id_sticker,)
            )
            
            registro = cursor.fetchone()
            if not registro:
                raise Exception("No se encontró un registro de ingreso activo para este vehículo")
                
            id_espacio_parqueo, fecha_hora_ingreso = registro
            
            # Registrar salida
            cursor.execute(
                """
                UPDATE vehiculos_espacio_parqueo
                SET fecha_hora_salida = %s
                WHERE id_espacio_parqueo = %s AND fecha_hora_ingreso = %s AND id_sticker = %s
                """, 
                (datetime.datetime.now(), id_espacio_parqueo, fecha_hora_ingreso, id_sticker)
            )
            
            # Actualizar estado del espacio a libre
            cursor.execute(
                "UPDATE espacios_parqueo SET id_estado = 1 WHERE id_espacio_parqueo = %s",  # 1 = libre
                (id_espacio_parqueo,)
            )
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al registrar salida: {e}")
        finally:
            cursor.close()
            conn.close()