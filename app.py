import streamlit as st
from controller import Controller

def main():
    # Inicializar controlador
    controller = Controller()
    
    # Inicializar estados de sesión
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Título principal de la aplicación
    st.title("Parking Pro - Sistema de Gestión de Parqueo Universitario")
    
    # Flujo para usuarios no autenticados
    if not st.session_state['logged_in']:
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab1:
            st.header("Iniciar Sesión")
            codigo_universitario = st.text_input("Código Universitario", key="login_codigo")
            
            if st.button("Iniciar Sesión", key="btn_login"):
                if controller.validar_login(codigo_universitario):
                    st.success(f"¡Bienvenido, {st.session_state['nombre_usuario']}!")
                    st.rerun()
                else:
                    st.error("Usuario no encontrado. Por favor regístrate primero.")
        
        with tab2:
            st.header("Registrarse")
            
            # Obtener tipos de usuarios para el menú desplegable
            tipos_usuarios = controller.obtener_tipos_usuarios()
            tipos_vehiculos = controller.obtener_tipos_vehiculos()
            
            # Formulario de registro
            codigo_universitario = st.text_input("Código Universitario", key="reg_codigo")
            nombre_usuario = st.text_input("Nombre completo")
            email_contacto = st.text_input("Correo electrónico")
            telefono_contacto = st.text_input("Teléfono de contacto")
            
            id_tipo_usuario = st.selectbox(
                "Tipo de usuario", 
                options=list(tipos_usuarios.keys()), 
                format_func=lambda x: tipos_usuarios[x]
            )
            
            # Datos del vehículo
            st.subheader("Datos del Vehículo")
            placa = st.text_input("Placa del vehículo (Máximo 7 caracteres)", max_chars=7)
            id_tipo_vehiculo = st.selectbox(
                "Tipo de vehículo",
                options=list(tipos_vehiculos.keys()),
                format_func=lambda x: tipos_vehiculos[x]
            )
            nombre_marca = st.text_input("Marca")
            nombre_modelo = st.text_input("Modelo")
            nombre_color = st.text_input("Color")
            
            if st.button("Registrarse", key="btn_register"):
                if controller.agregar_usuario_y_vehiculo(
                    codigo_universitario, nombre_usuario, email_contacto, 
                    telefono_contacto, id_tipo_usuario, placa, 
                    id_tipo_vehiculo, nombre_marca, nombre_modelo, nombre_color
                ):
                    st.success("¡Registro exitoso!")
                    # Re-validar para establecer la sesión
                    controller.validar_login(codigo_universitario)
                    st.rerun()
    
    # Flujo para usuarios autenticados
    else:
        # Menú lateral para navegación
        menu = st.sidebar.selectbox(
            "Menú",
            ["Ver Parqueo", "Mi Vehículo", "Registrar Ingreso/Salida", "Cerrar Sesión"]
        )
        
        # Mostrar nombre de usuario en sidebar
        st.sidebar.info(f"Usuario: {st.session_state.get('nombre_usuario', '')}")
        
        if menu == "Ver Parqueo":
            controller.mostrar_parqueo()
        
        elif menu == "Mi Vehículo":
            controller.mostrar_mi_vehiculo(st.session_state.get('user_id'))
            
        elif menu == "Registrar Ingreso/Salida":
            controller.registrar_ingreso_salida(st.session_state.get('user_id'))
            
        elif menu == "Cerrar Sesión":
            if st.sidebar.button("Confirmar Cierre de Sesión"):
                # Limpiar variables de sesión
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state['logged_in'] = False
                st.rerun()

if __name__ == "__main__":
    main()