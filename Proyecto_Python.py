# -*- coding: utf-8 -*-
"""
 --- CONSIDERACIONES IMPORTANTES ---
No olvides definir correctamente el directorio de trabajo y dejar ahí los archivos csv.
Todo lo que exportarás se irá directo a ese directorio de trabajo.
"""




"""
Parte 1) Data cleaning y Data preparation
- En este apartado prepararemos la data para nuestro trabajo
- Definimos la ruta local como directorio de trabajo
- Debemos instalar las librerías correspondientes (fuzz principalmente)
    - pip install thefuzz

"""

# Cargamos las librerías
import os
import pandas as pd
from thefuzz import fuzz, process



# Definimos el directorio de trabajo
directorio = os.path.dirname(os.path.abspath(__file__))
os.chdir(directorio) 


# Verificamos el directorio
print("Directorio actual:", os.getcwd())



# Cargamos los datos
df_ventas = pd.read_csv("Ventas.csv")
df_vendedores = pd.read_csv("Vendedores.csv")



# Convertimos los nombres de las empresas a minúsculas para evitar problemas de formato
df_ventas["empresa"] = df_ventas["empresa"].str.lower().str.strip()
df_vendedores["empresa"] = df_vendedores["empresa"].str.lower().str.strip()



def reverse_text(text):
    """Invierte el texto carácter por carácter"""
    if pd.isna(text):
        return text
    return text[::-1].strip()

# Creamos una función mejorada para encontrar la mejor coincidencia
def encontrar_mejor_match(nombre, lista_empresas):
    """
    Encuentra la mejor coincidencia usando múltiples métodos de fuzzy matching
    con un umbral más estricto para mayor precisión
    Incluye manejo especial para texto invertido
    """
    # Método 1: Matching normal (como antes)
    mejor_match, score_token = process.extractOne(nombre, lista_empresas, scorer=fuzz.token_sort_ratio)
    match_simple, score_simple = process.extractOne(nombre, lista_empresas, scorer=fuzz.ratio)
    match_partial, score_partial = process.extractOne(nombre, lista_empresas, scorer=fuzz.partial_ratio)
    
    # Método 2: Intentar con texto invertido (nuevo)
    nombre_invertido = reverse_text(nombre)
    mejor_match_invertido, score_invertido = process.extractOne(nombre_invertido, lista_empresas, scorer=fuzz.token_sort_ratio)
    
    # Comparar todos los scores
    scores = [
        (mejor_match, score_token, "normal_token"),
        (match_simple, score_simple, "normal_simple"),
        (match_partial, score_partial, "normal_partial"),
        (mejor_match_invertido, score_invertido, "invertido")
    ]
    
    # Ordenar por score (descendente)
    scores.sort(key=lambda x: x[1], reverse=True)
    mejor_match_final, mejor_score, metodo_usado = scores[0]
    
    # Umbral ajustado según método
    if metodo_usado == "invertido":
        # Para texto invertido, podemos ser más permisivos (umbral 40)
        if mejor_score >= 40:
            return mejor_match_final
    else:
        # Para texto normal, mantener umbral estricto (60)
        if mejor_score >= 60:
            return mejor_match_final
        elif mejor_score >= 50:
            # Validación adicional para scores borderline
            if len(scores) > 1:
                segundo_mejor_score = scores[1][1]
                # Si la diferencia es grande (>15 puntos), aceptar el match
                if mejor_score - segundo_mejor_score > 15:
                    return mejor_match_final
    
    return None  # No hay match confiable



# Aplicamos la función para encontrar la mejor coincidencia
# Creamos una nueva columna llamada "empresa_corregida"
# Aplicamos la función sobre df_ventas["empresa"] (Esta es la columna que tiene errores)
# apply aplica la función en cada fila de la columna indicada, es decir, va fila a fila evaluando
# x representa el nombre de la empresa en df_ventas["empresa"]
# x va tomando el valor de cada fila dentro de la columna df_ventas["empresa"]

def aplicar_match_con_debug(x, lista_empresas):
    resultado = encontrar_mejor_match(x, lista_empresas)
    if resultado is None:
        print(f"⚠️  Sin match para: '{x}'")
    return resultado

print("\n=== PROCESO DE MATCHING ===")
df_ventas["empresa_corregida"] = df_ventas["empresa"].apply(lambda x: aplicar_match_con_debug(x, df_vendedores["empresa"].tolist()))
print("=== FIN DEL PROCESO DE MATCHING ===\n")

# Revisamos cómo quedó la data luego de la creación de la columna corregida
df_ventas.head(50)




# Unimos los DataFrames utilizando la nueva columna corregida
# Merge en pandas es equivalente a un Join en SQL
# En este caso es un left Join (df_ventas es la tabla izquierda, y tiene sentido ya que tiene más datos)
df_final = df_ventas.merge(df_vendedores, left_on="empresa_corregida", right_on="empresa", how="left").drop(columns=["empresa_y"])

# Revisamos cómo quedó la data luego de la unión
df_final.head()
# Veremos que hay varios casos que no cruzan, y si bajamos el porcentaje de precisión?
# Repitamos todo nuevamente al final del código, pero con un umbral menor


# Renombramos las columnas para ordenar lo que llevamos
df_final.rename(columns={"empresa_x": "empresa_original", "empresa_corregida": "empresa_correcta"}, inplace=True)

# Filtramos los registros sin coincidencia
df_sin_match = df_final[df_final["empresa_correcta"].isna()]



# Guardamos los resultados en un CSV en la carpeta original
# Especificamos el separador para evitar problemas de lectura
df_final.to_csv("resultados_cruce.csv", index=False, sep=";")
df_sin_match.to_csv("registros_sin_cruce.csv", index=False, sep=";")





"""
Parte 2) Data Reporting y Data Visualization

- Debemos instalar las librerías correspondientes (fpdf principalmente)
    - pip install fpdf 
"""
import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd
from datetime import datetime


# 1. Calculamos el monto vendido por empresa
# Crearemos una nueva data con la información necesaria, ya que la necesitaremos para las gráficas
ventas_por_empresa = df_final.groupby("empresa_correcta")["monto"].sum().reset_index()
ventas_por_empresa = ventas_por_empresa.dropna().sort_values(by="monto", ascending=False)



# 2. Calculamos el monto vendido por vendedor
# Crearemos una nueva data con la información necesaria, ya que la necesitaremos para las gráficas
ventas_por_vendedor = df_final.groupby("vendedor")["monto"].sum().reset_index()
ventas_por_vendedor = ventas_por_vendedor.dropna().sort_values(by="monto", ascending=False)



# 3. Creamos gráficos y los guardamos
# Monto vendido por empresa
plt.figure(figsize=(10, 5))
plt.barh(ventas_por_empresa["empresa_correcta"], ventas_por_empresa["monto"], color='skyblue')
plt.xlabel("Monto Vendido")
plt.ylabel("Empresa")
plt.title("Monto Vendido por Empresa")
plt.gca().invert_yaxis() # Invierte el orden de los valores de la gráfica
plt.savefig("ventas_por_empresa.png", bbox_inches='tight')  # Guardar imagen y elimina espacios en blanco
plt.close()

# Monto vendido por vendedor
plt.figure(figsize=(10, 5))
plt.barh(ventas_por_vendedor["vendedor"], ventas_por_vendedor["monto"], color='orange')
plt.xlabel("Monto Vendido")
plt.ylabel("Vendedor")
plt.title("Monto Vendido por Vendedor")
plt.gca().invert_yaxis() # Invierte el orden de los valores de la gráfica
plt.savefig("ventas_por_vendedor.png", bbox_inches='tight')  # Guardar imagen y elimina espacios en blanco
plt.close()



# 4. Creamos el PDF
pdf = FPDF() # Crea un objeto PDF vacío
pdf.set_auto_page_break(auto=True, margin=15) #Añade nuevas páginas si es necesario, con un margen de 15
pdf.add_page() #Añade una nueva página al PDF, es obligatorio



# 5. Agregamos el título al PDF
pdf.set_font("Arial", style="B", size=16) # Fuente Arial, negrita, de tamaño 16
fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
titulo = f"Reporte de Ventas - {fecha_hora_actual}"

pdf.cell(200, 10, titulo, ln=True, align="C") # Crea una celda con el texto
# Ancho, alto, texto, salto de línea, centrado
pdf.ln(10) # Añade un espacio en blanco de 10



# 6. Agregamos la tabla de ventas por empresa
# Añadimos el título a la tabla                                                             a la tabla
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, "Monto Vendido por Empresa", ln=True, align="C")
pdf.ln(5) # Añade un espacio en blanco de 5

# Vamos celda por celda añadiendo los valores que necesitamos
# Es importante entender que estamos trabajando con celdas y las vamos rellenando
# Cada fila de la data se va añadiendo a una nueva celda
for index, row in ventas_por_empresa.iterrows(): # .iterrows() Indica que se recorrerá fila a fila
    pdf.cell(100, 10, row["empresa_correcta"], border=1) # Crea una celda y no hace salto de línea
    # border=1 indica que se añade un borde a la celda
    pdf.cell(50, 10, f"${row['monto']:.2f}", border=1, ln=True) # Crea una celda y hace salto de línea

pdf.ln(10)



# 7. Agregamos la tabla de ventas por vendedor
# No es necesario volver a definir el font
pdf.cell(200, 10, "Monto Vendido por Vendedor", ln=True, align="C")
pdf.ln(5)

for index, row in ventas_por_vendedor.iterrows():
    pdf.cell(100, 10, row["vendedor"], border=1)
    pdf.cell(50, 10, f"${row['monto']:.2f}", border=1, ln=True)

pdf.ln(10)



# 8. Insertamos los gráficos en el PDF
pdf.cell(200, 10, "Grafico: Monto Vendido por Empresa", ln=True, align="C")
pdf.image("ventas_por_empresa.png", x=10, w=180)
pdf.ln(10)

pdf.cell(200, 10, "Grafico: Monto Vendido por Vendedor", ln=True, align="C")
pdf.image("ventas_por_vendedor.png", x=10, w=180)
pdf.ln(10)



# 9. Guardar PDF
pdf.output("reporte_ventas.pdf") # Lo guarda con el nombre entregado

print("✅ PDF generado con éxito: reporte_ventas.pdf")





"""
Parte 3) Conclusiones

- Lo que acabamos de hacer es extremadamente útil en un proceso de automatización
- Esta es una entre muchas formas de crear documentos en Python
- De hecho, podemos tener un word estándar y modificar solo cierto valores del documento


"""





