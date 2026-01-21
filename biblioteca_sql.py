import re
import uuid
# Importamos el motor SQL
from sqlalchemy import create_engine, Column, String, Integer, func 
from sqlalchemy.orm import declarative_base, sessionmaker

# ==============================
# CONFIGURACIÓN SQL (El Motor)
# ==============================
# 1. Crear el molde
Base = declarative_base()

# 2. Definir la Tabla (Tu Clase Libro evolucionada)
class Libro(Base):
    __tablename__ = 'libros' # Nombre de la tabla en el archivo

    id = Column(String, primary_key=True)
    nombre = Column(String)
    categoria = Column(String)
    autor = Column(String)
    editorial = Column(String)
    paginas = Column(Integer)
    cantidad = Column(Integer)

    def __init__(self, nombre, categoria, autor, editorial, paginas, cantidad):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.categoria = categoria
        self.autor = autor
        self.editorial = editorial
        self.paginas = paginas
        self.cantidad = cantidad

    #Propiedad para el Frontend (CSS)
    @property
    def clase_css_stock(self):
        return "stock-bajo" if self.cantidad < 5 else "stock-alto"
        

# 3. Encender el motor
# echo=False para que no nos llene la pantalla de texto técnico
motor = create_engine('sqlite:///biblioteca_produccion.sqlite', echo=False) 
Base.metadata.create_all(motor)

# 4. Crear la Sesión (Nuestra conexión permanente)
Session = sessionmaker(bind=motor)
session = Session()

# ==============================
# COLORES Y UTILIDADES
# ==============================
RED, GREEN, BLUE, RESET = "\033[91m", "\033[92m", "\033[94m", "\033[0m"

# ==============================
# LÓGICA DE NEGOCIO (SQL)
# ==============================

def buscar_libro_unico(nombre: str, editorial: str):
    """
    Busca en la BD ignorando mayúsculas/minúsculas y espacios extra.
    Devuelve el objeto Libro o None si no lo encuentra.
    """
    nombre_usuario = nombre.strip().lower()
    editorial_usuario = editorial.strip().lower()

    # session.query(Modelo).filter(...).first() devuelve el objeto o None
    return session.query(Libro).filter(
        func.lower(Libro.nombre) == nombre_usuario,
        func.lower(Libro.editorial) == editorial_usuario
    ).first()

def registrar_libro_sql():
    print(f"\n{BLUE}--- Nuevo Registro SQL ---{RESET}")
    # 1. Pedimos Nombre y Editorial primero
    nombre = input("Nombre: ").strip()
    editorial = input("Editorial: ").strip()

    # 2. VERIFICACIÓN EN TIEMPO REAL
    # Antes de pedir más datos, miramos si ya existe en la BD
    existe = buscar_libro_unico(nombre, editorial)
    
    if existe:
        print(f"\n{BLUE}¡El libro ya existe en la Base de Datos!{RESET}")
        print(f"Stock actual: {existe.cantidad}")
        sumar = input("¿Desea sumar stock? (si/no): ").lower()
        if sumar == "si":
            while True:
                try:
                    cant = int(input("Cantidad a sumar: "))
                    if cant > 0:
                        existe.cantidad += cant # SQL Alchemy detecta el cambio
                        session.commit() # ¡GUARDADO!
                        print(f"{GREEN}Stock actualizado.{RESET}")
                        break
                    print("Deber ser mayor a 0.")
                    
                except ValueError:
                    print(f"{RED}Error: Ingrese un número entero.{RESET}")
        return
            
    # Si no existe, pedimos el resto
    categoria = input("Categoría: ").strip()
    autor = input("Autor: ").strip()
    # ... después de pedir autor ...

    # Validación de Páginas
    while True:
        try:
            paginas = int(input("Páginas: "))
            if paginas > 0: break
            print(f"{RED}Debe ser mayor a 0.{RESET}")
        except ValueError:
            print(f"{RED}Error: Ingrese un número entero.{RESET}")

    # Validación de Cantidad
    while True:
        try:
            cantidad = int(input("Cantidad inicial: "))
            if cantidad >= 0: break
            print(f"{RED}Debe ser mayor a 0.{RESET}")
        except ValueError:
            print(f"{RED}Error: Ingrese un número entero.{RESET}")
    
    # CREAR (Insert)
    nuevo_libro = Libro(nombre, categoria, autor, editorial, paginas, cantidad)
    # ...

    # CREAR (Insert)
    try:
        nuevo_libro = Libro(nombre, categoria, autor, editorial, paginas, cantidad)
        session.add(nuevo_libro)
        session.commit() # ¡GUARDADO PERMANENTE!
        print(f"{GREEN}Libro guardado en SQLite con ID: {nuevo_libro.id}{RESET}")
    except Exception as e:
        session.rollback() # En caso de error, revertir cambios
        print(f"{RED}Error al guardar el libro: {e}{RESET}")

def ver_catalogo_sql():
    # LEER (Select All)
    # session.query(Libro).all() trae TODA la tabla convertida en objetos
    libros = session.query(Libro).all()
    
    if not libros:
        print("La base de datos está vacía.")
        return

    print("=" * 120)
    print(f"\n                                            CATÁLOGO DE LIBROS ")
    print("=" * 120)
    print(f"\n{'TÍTULO':<40} | {'CATEGORIA':<15} | {'AUTOR':<15} | {'EDITORIAL':<15} | {'PÁGINAS':<15} | STOCK")
    print("-" * 120)
    for l in libros:
        print(f"{l.nombre:<40} | {l.categoria:<15} | {l.autor:<15} | {l.editorial:<15} | {l.paginas:<15} | {l.cantidad}")

def eliminar_libro_sql():
    nombre = input("Nombre exacto: ")
    editorial = input("Editorial exacta: ")
    
    libro = buscar_libro_unico(nombre, editorial)
    
    if libro:
        confirmar = input(f"¿Eliminar '{libro.nombre}'? (si/no): ")
        if confirmar == "si":
            session.delete(libro) # BORRAR (Delete)
            session.commit()      # Confirmar borrado
            print(f"{GREEN}Eliminado de la BD.{RESET}")
    else:
        print(f"{RED}No encontrado.{RESET}")

def filtrar_sql():
    print(f"\n{BLUE}--- Búsqueda Avanzada ---{RESET}")
    print("1. Buscar por Nombre")
    print("2. Buscar por Categoría")
    
    op = input(">>> Seleccione opción (1-2): ").strip()
    
    # 1. VALIDACIÓN: Si no es 1 ni 2, cortamos el proceso AQUI.
    if op not in ["1", "2"]:
        print(f"{RED}Error: Opción desconocida. Regresando al menú.{RESET}")
        return # <--- ¡STOP! Salimos de la función inmediatamente.

    # 2. Solo si pasó la validación, pedimos el término
    term = input("Ingrese término a buscar: ").strip()
    
    resultados = []
    
    # Usamos .ilike() en lugar de .contains() para que ignore mayúsculas/minúsculas
    # (SQLAlchemy traduce ilike a una búsqueda flexible)
    if op == "1":
        resultados = session.query(Libro).filter(Libro.nombre.ilike(f"%{term}%")).all()
    elif op == "2":
        resultados = session.query(Libro).filter(Libro.categoria.ilike(f"%{term}%")).all()
        
    # 3. Reporte de Resultados
    if resultados:
        print(f"\n{GREEN}Se encontraron {len(resultados)} libros:{RESET}")
        print("-" * 40)
        print(f"\n {'TÍTULO':<15} | {'EDITORIAL':<5} | STOCK")
        print("-" * 40)
        for l in resultados:
            print(f"📖 {l.nombre} | ({l.editorial}) | {l.cantidad}")
    else:
        print(f"{RED}No se encontraron libros que coincidan con '{term}'.{RESET}")

# ==============================
# MENÚ PRINCIPAL
# ==============================
def main():
    while True:
        print("\n" + "="*30)
        print("      🏛️ BIBLIOTECA SQL")
        print("-" * 30)
        print("1. Registrar (Create)")
        print("2. Ver Catálogo (Read)")
        print("3. Buscar (Filter)")
        print("4. Eliminar (Delete)")
        print("5. Salir")
        
        op = input(">>> ")
        
        if op == "1": registrar_libro_sql()
        elif op == "2": ver_catalogo_sql()
        elif op == "3": filtrar_sql()
        elif op == "4": eliminar_libro_sql()
        elif op == "5": 
            print("Cerrando conexión SQL...")
            session.close() # Buenas prácticas: Cerrar al salir
            break

if __name__ == "__main__":
    main()