import streamlit as st
import pandas as pd
import plotly.graph_objects as go

class View:
    def __init__(self):
        """Inicializa la vista"""
        pass
        
    def mostrar_titulo_seccion(self, titulo):
        """Muestra un título de sección con formato estandarizado"""
        st.header(titulo)
        st.markdown("---")
        
    def mostrar_mapa_parqueo(self, df_parqueo):
        """
        Muestra un mapa visual del parqueo utilizando Plotly
        """
        st.subheader("Mapa del Parqueo")
        
        # Crear un mapa personalizado según las secciones
        fig = go.Figure()
        
        # Mapeo de colores según el estado
        colores = {
            1: 'green',  # Libre
            2: 'red',    # Ocupado
            3: 'gray'    # No disponible
        }
        
        # Agrupar por sección para organizar la visualización
        for seccion in df_parqueo['id_seccion'].unique():
            seccion_df = df_parqueo[df_parqueo['id_seccion'] == seccion]
            
            # Calcular posiciones para cada espacio (simuladas)
            # En una implementación real, podrías tener coordenadas específicas para cada espacio
            espacios_count = len(seccion_df)
            cols = min(5, espacios_count)  # Máximo 5 espacios por fila
            rows = (espacios_count // cols) + (1 if espacios_count % cols > 0 else 0)
            
            for idx, (_, espacio) in enumerate(seccion_df.iterrows()):
                row = idx // cols
                col = idx % cols
                
                # Desplazamiento por sección
                if seccion == 'A':
                    x_offset, y_offset = 0, 0
                elif seccion == 'B':
                    x_offset, y_offset = 8, 0
                elif seccion == 'C':
                    x_offset, y_offset = 0, 8
                elif seccion == 'D':
                    x_offset, y_offset = 8, 8
                else:
                    x_offset, y_offset = 16, 0
                
                # Crear rectángulo para representar el espacio
                color = colores.get(espacio['id_estado'], 'blue')
                
                # Texto para el hover
                texto = (f"Espacio: {espacio['id_espacio_parqueo']}<br>"
                         f"Estado: {espacio['nombre_estado']}<br>"
                         f"Sección: {espacio['nombre_seccion']}")
                
                # Agregar rectángulo al mapa
                fig.add_shape(
                    type="rect",
                    x0=col + x_offset,
                    y0=row + y_offset,
                    x1=col + 0.9 + x_offset,
                    y1=row + 0.9 + y_offset,
                    line=dict(color="black", width=1),
                    fillcolor=color,
                    opacity=0.7,
                )
                
                # Agregar número de espacio
                fig.add_annotation(
                    x=col + 0.45 + x_offset,
                    y=row + 0.45 + y_offset,
                    text=str(espacio['id_espacio_parqueo']),
                    showarrow=False,
                    font=dict(color="white" if color == "red" else "black", size=10)
                )
            
            # Agregar etiqueta de sección
            fig.add_annotation(
                x=x_offset,
                y=y_offset - 0.5,
                text=f"Sección {seccion}",
                showarrow=False,
                font=dict(size=14, color="black"),
                xanchor="left"
            )
        
        # Configurar el layout
        fig.update_layout(
            title="Distribución de Espacios",
            autosize=True,
            height=600,
            showlegend=False,
            plot_bgcolor='white',
            margin=dict(l=20, r=20, t=60, b=20),
        )
        
        # Configurar los ejes
        fig.update_xaxes(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        )
        
        fig.update_yaxes(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
        )
        
        # Mostrar el mapa
        st.plotly_chart(fig, use_container_width=True)
        
        # Agregar leyenda
        legend_col1, legend_col2, legend_col3 = st.columns(3)
        with legend_col1:
            st.markdown("🟢 Libre")
        with legend_col2:
            st.markdown("🔴 Ocupado")
        with legend_col3:
            st.markdown("⚪ No disponible")
    
    def mostrar_tabla_parqueo(self, df_parqueo):
        """
        Muestra una tabla con información detallada del parqueo
        """
        # Formatear los datos para la tabla
        tabla_df = df_parqueo[['id_espacio_parqueo', 'nombre_seccion', 'nombre_estado']].copy()
        tabla_df.columns = ['ID Espacio', 'Sección', 'Estado']
        
        # Aplicar formato condicional
        def highlight_estado(val):
            if val == 'Libre':
                return 'background-color: #a6f5a6'  # Verde claro
            elif val == 'Ocupado':
                return 'background-color: #f5a6a6'  # Rojo claro
            else:
                return 'background-color: #e0e0e0'  # Gris claro
                
        # Mostrar tabla con formato
        st.dataframe(
            tabla_df.style.applymap(highlight_estado, subset=['Estado']),
            use_container_width=True
        )
    
    def mostrar_detalle_vehiculo(self, vehiculo):
        """
        Muestra los detalles del vehículo del usuario
        """
        if not vehiculo:
            st.warning("No tienes vehículos registrados.")
            return
            
        # Crear un diseño de tarjeta para la información del vehículo
        st.subheader("Información de mi Vehículo")
        
        # Usar columnas para un diseño más agradable
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Sticker:** #{vehiculo['id_sticker']}")
            st.markdown(f"**Placa:** {vehiculo['placa']}")
            st.markdown(f"**Tipo:** {vehiculo['nombre_tipo_vehiculo']}")
        
        with col2:
            st.markdown(f"**Marca:** {vehiculo['nombre_marca']}")
            st.markdown(f"**Modelo:** {vehiculo['nombre_modelo']}")
            st.markdown(f"**Color:** {vehiculo['nombre_color']}")
        
        # Añadir un separador
        st.markdown("---")
        
    def mostrar_formulario_actualizar_vehiculo(self, vehiculo, tipos_vehiculos):
        """
        Muestra el formulario para actualizar la información del vehículo
        """
        st.subheader("Actualizar información")
        
        # Preparar datos del formulario con los valores actuales
        placa = st.text_input("Placa del vehículo", value=vehiculo['placa'], max_chars=7)
        
        id_tipo_vehiculo = st.selectbox(
            "Tipo de vehículo",
            options=list(tipos_vehiculos.keys()),
            format_func=lambda x: tipos_vehiculos[x],
            index=list(tipos_vehiculos.keys()).index(vehiculo['id_tipo_vehiculo']) if vehiculo['id_tipo_vehiculo'] in tipos_vehiculos else 0
        )
        
        nombre_marca = st.text_input("Marca", value=vehiculo['nombre_marca'])
        nombre_modelo = st.text_input("Modelo", value=vehiculo['nombre_modelo'])
        nombre_color = st.text_input("Color", value=vehiculo['nombre_color'])
        
        # Devolver los datos actualizados como un diccionario
        return {
            'placa': placa,
            'id_tipo_vehiculo': id_tipo_vehiculo,
            'nombre_marca': nombre_marca,
            'nombre_modelo': nombre_modelo,
            'nombre_color': nombre_color
        }
        
    def mostrar_formulario_ingreso(self, espacios_disponibles):
        """
        Muestra el formulario para registrar el ingreso de un vehículo
        """
        if espacios_disponibles.empty:
            st.warning("No hay espacios disponibles en este momento.")
            return None
            
        # Mostrar información sobre espacios disponibles
        st.info(f"Hay {len(espacios_disponibles)} espacios disponibles.")
        
        # Permitir seleccionar espacio
        opciones_espacios = espacios_disponibles['id_espacio_parqueo'].tolist()
        id_espacio = st.selectbox(
            "Selecciona un espacio disponible", 
            opciones_espacios
        )
        
        return id_espacio
        
    def mostrar_formulario_salida(self, vehiculo_en_parqueo):
        """
        Muestra el formulario para registrar la salida de un vehículo
        """
        st.info(f"Tu vehículo está actualmente en el espacio #{vehiculo_en_parqueo['id_espacio_parqueo']}")
        
        # Mostrar información sobre tiempo de estadía
        from datetime import datetime
        ingreso = vehiculo_en_parqueo['fecha_hora_ingreso']
        tiempo_actual = datetime.now()
        
        duracion = tiempo_actual - ingreso
        horas = duracion.seconds // 3600
        minutos = (duracion.seconds % 3600) // 60
        
        st.markdown(f"**Tiempo de estadía:** {horas} horas y {minutos} minutos")
        
        return st.button("Registrar Salida")