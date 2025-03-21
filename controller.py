import streamlit as st
from model import Database
from view import View

class Controller:
    def __init__(self):
        self.model = Database()
        self.view = View()

    def validar_login(self, codigo_universitario):
        """Valida el código universitario y establece la sesión del usuario"""
        if not codigo_universitario:
            return False
            
        usuario = self.model.obtener_usuario_por_codigo(codigo_universitario)
        if usuario:
            # Establecer variables de sesión
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = usuario['id_usuario']
            st.session_state['codigo_universitario'] = usuario['codigo_universitario']
            st.session_state['nombre_usuario'] = usuario['nombre_usuario']
            st.session_state['id_tipo_usuario'] = usuario['id_tipo_usuario']
            return True
        return False

    def obtener_tipos_usuarios(self):
        """Obtiene los tipos de usuarios disponibles"""
        return self.model.obtener_tipos_usuarios()
        
    def obtener_tipos_vehiculos(self):
        """Obtiene los tipos de vehículos disponibles"""
        return self.model.obtener_tipos_vehiculos()
        
    def agregar_usuario_y_vehiculo(self, codigo_universitario, nombre_usuario, email_contacto, 
                                 telefono_contacto, id_tipo_usuario, placa, 
                                 id_tipo_vehiculo, nombre_marca, nombre_modelo, nombre_color):
        """Agrega un nuevo usuario con su vehículo al sistema"""
        # Validaciones básicas
        if not codigo_universitario or not nombre_usuario or not placa:
            st.error("Todos los campos son obligatorios")
            return False
            
        try:
            self.model.agregar_usuario(
                codigo_universitario, nombre_usuario, email_contacto, 
                telefono_contacto, id_tipo_usuario, placa, 
                id_tipo_vehiculo, nombre_marca, nombre_modelo, nombre_color
            )
            return True
        except Exception as e:
            st.error(f"Error al registrar: {e}")
            return False

    def mostrar_parqueo(self):
        """Muestra el estado actual del parqueo"""
        self.view.mostrar_titulo_seccion("Estado Actual del Parqueo")
        
        # Obtener datos del parqueo
        parqueo_df = self.model.obtener_parqueo()
        
        if parqueo_df.empty:
            st.warning("No se pudieron cargar los datos del parqueo. Verifica la conexión a la base de datos.")
            return
            
        # Filtrar espacios por tipo de usuario y vehículo
        id_tipo_usuario = st.session_state.get('id_tipo_usuario')
        info_vehiculo = self.model.obtener_vehiculo_por_usuario(st.session_state.get('user_id'))
        
        if not info_vehiculo:
            st.warning("No tienes vehículos registrados.")
            return
            
        id_tipo_vehiculo = info_vehiculo['id_tipo_vehiculo']
        
        # Determinar secciones permitidas según el tipo de usuario y vehículo
        secciones_permitidas = self._determinar_secciones_permitidas(id_tipo_usuario, id_tipo_vehiculo)
        
        # Filtrar parqueo por secciones permitidas
        parqueo_filtrado = parqueo_df[parqueo_df['id_seccion'].isin(secciones_permitidas)]
        
        # Mostrar estadísticas
        total_espacios = len(parqueo_filtrado)
        espacios_libres = len(parqueo_filtrado[parqueo_filtrado['id_estado'] == 1])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Espacios Disponibles", espacios_libres)
        with col2:
            st.metric("Ocupación", f"{100 - (espacios_libres/total_espacios*100):.1f}%")
        
        # Mostrar visualización del parqueo
        self.view.mostrar_mapa_parqueo(parqueo_filtrado)
        
        # Mostrar tabla filtrada de espacios
        with st.expander("Ver detalles de espacios", expanded=False):
            self.view.mostrar_tabla_parqueo(parqueo_filtrado)

    def _determinar_secciones_permitidas(self, id_tipo_usuario, id_tipo_vehiculo):
        """Determina las secciones permitidas según el tipo de usuario y vehículo"""
        secciones_permitidas = []
        
        # Reglas de negocio para asignar secciones
        if id_tipo_vehiculo == 1:  # Motocicleta
            secciones_permitidas = ['D']
        else:  # Automóvil
            if id_tipo_usuario == 1:  # Estudiante
                secciones_permitidas = ['C', 'A', 'B']
            elif id_tipo_usuario == 2:  # Profesor
                secciones_permitidas = ['B']
            elif id_tipo_usuario == 3:  # Administrativo
                secciones_permitidas = ['A']
                
        return secciones_permitidas

    def mostrar_mi_vehiculo(self, id_usuario):
        """Muestra información del vehículo del usuario"""
        self.view.mostrar_titulo_seccion("Mi Vehículo")
        
        vehiculo = self.model.obtener_vehiculo_por_usuario(id_usuario)
        
        if not vehiculo:
            st.warning("No tienes vehículos registrados.")
            return
            
        self.view.mostrar_detalle_vehiculo(vehiculo)
        
        # Opción para actualizar información del vehículo
        if st.checkbox("Actualizar información del vehículo"):
            tipos_vehiculos = self.model.obtener_tipos_vehiculos()
            datos_actualizados = self.view.mostrar_formulario_actualizar_vehiculo(vehiculo, tipos_vehiculos)
            
            if st.button("Guardar Cambios"):
                try:
                    self.model.actualizar_vehiculo(
                        id_usuario, 
                        datos_actualizados['placa'],
                        datos_actualizados['id_tipo_vehiculo'],
                        datos_actualizados['nombre_marca'],
                        datos_actualizados['nombre_modelo'],
                        datos_actualizados['nombre_color']
                    )
                    st.success("¡Vehículo actualizado correctamente!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar: {e}")

    def registrar_ingreso_salida(self, id_usuario):
        """Registra el ingreso o salida de un vehículo"""
        self.view.mostrar_titulo_seccion("Registrar Ingreso/Salida")
        
        # Verificar si tiene vehículo registrado
        vehiculo = self.model.obtener_vehiculo_por_usuario(id_usuario)
        
        if not vehiculo:
            st.warning("No tienes vehículos registrados.")
            return
            
        # Verificar si el vehículo está actualmente en el parqueo
        vehiculo_en_parqueo = self.model.verificar_vehiculo_en_parqueo(vehiculo['id_sticker'])
        
        if vehiculo_en_parqueo:
            # Mostrar opción de salida
            st.info(f"Tu vehículo está actualmente en el espacio #{vehiculo_en_parqueo['id_espacio_parqueo']}")
            
            if st.button("Registrar Salida"):
                if self.model.registrar_salida(vehiculo['id_sticker']):
                    st.success("¡Salida registrada correctamente!")
                    st.rerun()
                else:
                    st.error("Error al registrar la salida.")
        else:
            # Mostrar opción de ingreso
            parqueo_df = self.model.obtener_parqueo()
            
            # Filtrar espacios disponibles según tipo de usuario y vehículo
            id_tipo_usuario = st.session_state.get('id_tipo_usuario')
            id_tipo_vehiculo = vehiculo['id_tipo_vehiculo']
            
            secciones_permitidas = self._determinar_secciones_permitidas(id_tipo_usuario, id_tipo_vehiculo)
            
            # Filtrar solo espacios libres
            espacios_disponibles = parqueo_df[
                (parqueo_df['id_seccion'].isin(secciones_permitidas)) & 
                (parqueo_df['id_estado'] == 1)
            ]
            
            if espacios_disponibles.empty:
                st.warning("No hay espacios disponibles en este momento.")
                return
                
            # Permitir seleccionar espacio
            opciones_espacios = espacios_disponibles['id_espacio_parqueo'].tolist()
            id_espacio = st.selectbox("Selecciona un espacio disponible", opciones_espacios)
            
            if st.button("Registrar Ingreso"):
                if self.model.registrar_ingreso(vehiculo['id_sticker'], id_espacio):
                    st.success(f"¡Ingreso registrado correctamente en el espacio #{id_espacio}!")
                    st.rerun()
                else:
                    st.error("Error al registrar el ingreso.")