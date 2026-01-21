from flask import Flask, flash
from datetime import datetime
import json
import pandas as pd
import io # Para manejo de flujos de datos en memoria RAM
from flask import Blueprint, render_template, request, redirect, send_file
from biblioteca_sql import session, Libro
import math
from sqlalchemy import or_

# 1. Creamos el Blueprint (El "Módulo" de rutas)
# Lo llamamos 'global' porque manejará las rutas generales
rutas_globales = Blueprint('global', __name__)

# 2. DEFINIMOS LAS RUTAS USANDO EL BLUEPRINT
# Fíjate que ahora es @rutas_globales.route, NO @app.route

@rutas_globales.route('/')
def inicio():
    return render_template('index.html')

@rutas_globales.route('/catalogo')
def ver_catalogo():
    # 1. CAPTURAR PARÁMETROS DE LA URL
    # ?page=1 (Por defecto página 1)
    page = request.args.get('page', 1, type=int) 
    # ?q=Harry (Por defecto vacío)
    busqueda = request.args.get('q', '', type=str) 
    
    # Configuración
    per_page = 20 # Libros por página
    
    # 2. CONSTRUIR LA CONSULTA BASE (Query Builder)
    query = session.query(Libro)
    
    # 3. APLICAR FILTRO DE BÚSQUEDA (Si el usuario escribió algo)
    if busqueda:
        # Busca si el texto está en el Nombre O en el Autor O en la Editorial
        query = query.filter(
            or_(
                Libro.nombre.ilike(f"%{busqueda}%"),
                Libro.autor.ilike(f"%{busqueda}%"),
                Libro.editorial.ilike(f"%{busqueda}%")
            )
        )
    
    # 4. MATEMÁTICAS DE PAGINACIÓN
    total_libros = query.count() # ¿Cuántos libros cumplen el filtro?
    total_pages = math.ceil(total_libros / per_page) # Redondeamos hacia arriba
    
    # Calcular el recorte (Offset)
    # Pág 1: Salta 0, toma 20.
    # Pág 2: Salta 20, toma 20.
    offset = (page - 1) * per_page
    
    # 5. EJECUTAR LA CONSULTA RECORTADA
    lista_libros = query.limit(per_page).offset(offset).all()
    
    # 6. ENVIAR TODO AL HTML
    return render_template('catalogo.html', 
                           libros=lista_libros, 
                           page=page, 
                           total_pages=total_pages,
                           busqueda=busqueda)

@rutas_globales.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        try:
            # Captura de datos
            nombre = request.form['nombre']
            categoria = request.form['categoria']
            autor = request.form['autor']
            editorial = request.form['editorial']
            paginas = int(request.form['paginas'])
            cantidad = int(request.form['cantidad'])
            
            # Guardado
            nuevo_libro = Libro(nombre, categoria, autor, editorial, paginas, cantidad)
            session.add(nuevo_libro)
            session.commit()

            flash("Libro registrado con éxito.", "success")
            return redirect('/catalogo')
        except ValueError:
            return "Error: Datos inválidos"
            
    return render_template('formulario.html')

@rutas_globales.route('/actualizar_stock', methods=['POST'])
def actualizar_stock():
    id_libro = request.form['id_libro']
    nuevo_stock = int(request.form['nuevo_stock'])
    libro = session.query(Libro).filter_by(id=id_libro).first()
    if libro:
        libro.cantidad = nuevo_stock
        session.commit()

        flash("Stock actualizado con éxito.", "info")
    return redirect('/catalogo')

@rutas_globales.route('/eliminar/<id>')
def eliminar_libro(id):
    libro = session.query(Libro).filter_by(id=id).first()
    if libro:
        session.delete(libro)
        session.commit()

        flash("Libro eliminado con éxito de la base de datos.", "warning")
    return redirect('/catalogo')

# Ruta para descargar el inventario en Excel 
@rutas_globales.route('/descargar_excel')
def descargar_excel():
    # 1. Consultamos todos los libros
    libros = session.query(Libro).all()
    
    # 2. Convertimos Objetos SQL -> Lista de Diccionarios (Para Pandas)
    lista_datos = []
    for l in libros:
        lista_datos.append({
            "Título": l.nombre,
            "Categoría": l.categoria,
            "Autor": l.autor,
            "Editorial": l.editorial,
            "Páginas": l.paginas,
            "Stock": l.cantidad,
            "ID Sistema": l.id
        })
        
    # 3. Creamos el DataFrame
    df = pd.read_json(json.dumps(lista_datos)) if not lista_datos else pd.DataFrame(lista_datos)
    # (Nota simple: pd.DataFrame(lista_datos) es suficiente si la lista no está vacía)
    
    if not lista_datos:
        return "No hay datos para descargar"

    df = pd.DataFrame(lista_datos)

    # 4. Magia de Ingeniero: Guardar en RAM (BytesIO)
    # En lugar de crear un archivo en tu disco, lo creamos en el aire.
    output = io.BytesIO()
    
    # Usamos ExcelWriter para guardar el df en el buffer 'output'
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario')
    
    # "Rebobinamos" el archivo al principio para poder leerlo y enviarlo
    output.seek(0)
    
    # 5. Generar nombre con fecha (Ej: biblioteca_2026-01-20.xlsx)
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"biblioteca_{fecha_hoy}.xlsx"

    # 6. Enviamos el archivo al navegador
    return send_file(
        output, 
        download_name=nombre_archivo, 
        as_attachment=True, # Esto fuerza la descarga
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )