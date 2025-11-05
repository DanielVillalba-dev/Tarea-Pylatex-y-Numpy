import numpy as np
from pylatex import Document, Tabular, Section, Subsection

class GeneracionMatrices:
    def __init__(self, i, j):
        self.i = i
        self.j = j

    def matrizFila(self):
        return np.random.randint(1, 100, size=(1, self.i))

    def matrizColumna(self):
        return np.random.randint(1, 100, size=(self.j, 1))

    def matrizCuadrada(self):
        n = min(self.i, self.j)
        return np.random.randint(1, 100, size=(n, n))

    def matrizRectangular(self):
        return np.random.randint(1, 100, size=(self.j, self.i))

    def matrizDiagonal(self):
        n = min(self.i, self.j)
        vector = np.random.randint(1, 100, size=n)
        return np.diag(vector)

    def matrizSuperior(self):
        matriz = np.random.randint(1, 100, size=(self.j, self.i))
        return np.triu(matriz)

    def matrizInferior(self):
        matriz = np.random.randint(1, 100, size=(self.j, self.i))
        return np.tril(matriz)

    def matrizIdentidad(self):
        n = min(self.i, self.j)
        return np.eye(n, dtype=int)

    def matrizNula(self):
        return np.zeros((self.j, self.i), dtype=int)

# Función para convertir una matriz numpy en una tabla de PyLaTeX
def matriz_a_tabla(matriz):
    filas, columnas = matriz.shape
    tabla = Tabular("|".join(["c"]*columnas))
    tabla.add_hline()
    for fila in matriz:
        tabla.add_row([int(x) for x in fila])
        tabla.add_hline()
    return tabla

doc = Document()

i, j = 4, 3
tipo_matriz = "triangular superior"

generacion =GeneracionMatrices(i, j)

if tipo_matriz == "fila":
    matriz = generacion.matrizFila()
elif tipo_matriz == "columna":
    matriz = generacion.matrizColumna()
elif tipo_matriz == "cuadrada":
    matriz = generacion.matrizCuadrada()
elif tipo_matriz == "rectangular":
    matriz = generacion.matrizRectangular()
elif tipo_matriz == "diagonal":
    matriz = generacion.matrizDiagonal()
elif tipo_matriz == "triangular superior":
    matriz = generacion.matrizSuperior()
elif tipo_matriz == "triangular inferior":
    matriz = generacion.matrizInferior()
elif tipo_matriz == "identidad":
    matriz = generacion.matrizIdentidad()
elif tipo_matriz == "nula":
    matriz = generacion.matrizNula()
else:
    raise ValueError("Tipo de matriz no válido")

with doc.create(Section(f"Matriz: {tipo_matriz}")):
    tabla = matriz_a_tabla(matriz)
    doc.append(tabla)

doc.generate_pdf("matriz_latex", clean_tex=False)
print("Documento generado: matriz_latex.pdf")