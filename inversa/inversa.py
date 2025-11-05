from pylatex import Document, Section, Subsection, NoEscape
from fractions import Fraction
import sys


def to_fraction_matrix(A):
    """Convierte una matriz (lista de listas) a Fraction en cada entrada."""
    return [[Fraction(x) for x in row] for row in A]

def minor_matrix(A, row, col):
    """Devuelve el menor de A eliminando la fila `row` y columna `col` (0-based)."""
    n = len(A)
    return [[A[r][c] for c in range(n) if c != col] for r in range(n) if r != row]

def det_recursive(A):
    """Calcula el determinante de A recursivamente (lista de listas de Fraction)."""
    n = len(A)
    if n == 0:
        return Fraction(1)
    if n == 1:
        return Fraction(A[0][0])
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    total = Fraction(0)
    for j in range(n):
        sign = Fraction(-1 if j % 2 == 1 else 1)
        # construir el menor sin la fila 0 y columna j
        minor = [[A[r][c] for c in range(n) if c != j] for r in range(1, n)]
        total += sign * A[0][j] * det_recursive(minor)
    return total

def cofactor(A, i, j):
    """Cofactor C_ij = (-1)^{i+j} * det(minor_ij), i,j 0-based."""
    sign = Fraction(-1 if ((i + j) % 2 == 1) else 1)
    m = minor_matrix(A, i, j)
    return sign * det_recursive(m)

def transpose(A):
    """Trasponer matriz A (lista de listas)."""
    return [list(row) for row in zip(*A)]

def multiply_scalar(A, scalar):
    """Multiplica cada entrada de A por el escalar dado."""
    return [[scalar * A[i][j] for j in range(len(A))] for i in range(len(A))]

def frac_to_latex(f: Fraction):
    """Convierte Fraction a LaTeX: entero o \frac{a}{b}."""
    if isinstance(f, Fraction):
        if f.denominator == 1:
            return str(f.numerator)
        return r"\frac{%d}{%d}" % (f.numerator, f.denominator)
    # si no es Fraction, devolver str
    return str(f)

def matriz_a_latex_bmatrix(A):
    """
    Convierte matriz (lista de listas) a cadena LaTeX con entorno bmatrix.
    Ejemplo de salida: \begin{bmatrix} 1 & \frac{1}{2} \\ 0 & 3 \end{bmatrix}
    """
    filas = []
    for fila in A:
        elems = [frac_to_latex(x) for x in fila]
        filas.append(" & ".join(elems))
    return r"\begin{bmatrix}" + r" \\ ".join(filas) + r"\end{bmatrix}"

def calcular_inversa_pasoaPaso(A_raw):
    """
    Realiza el cálculo por cofactores y prepara una lista de pasos en LaTeX.
    Devuelve:
      detA (Fraction), pasos (lista de tuplas (titulo, contenido_latex)), adj, inv
    """
    A = to_fraction_matrix(A_raw)
    n = len(A)
    pasos = []

    # Paso 1: Matriz original (mostrarla en display math)
    pasos.append(("Matriz original", NoEscape(r"\[ A \;=\; %s \]" % matriz_a_latex_bmatrix(A))))

    # Paso 2: Determinante de A (mostrar valor)
    detA = det_recursive(A)
    pasos.append(("Determinante", NoEscape(r"\[ \det(A) \;=\; %s \]" % frac_to_latex(detA))))

    # Si determinante cero → singularidad (no hay inversa)
    if detA == 0:
        pasos.append(("Matriz singular", NoEscape(r"La matriz es singular: \(\det(A)=0\). No existe la inversa.")))
        return detA, pasos, None, None

    # Paso 3: Calcular menores, determinantes de menores y cofactores
    cofactor_matrix = [[None] * n for _ in range(n)]
    contenido_menores = []
    for i in range(n):
        for j in range(n):
            Mij = minor_matrix(A, i, j)
            detMij = det_recursive(Mij)
            Cij = cofactor(A, i, j)
            cofactor_matrix[i][j] = Cij

            # Formatear cada menor y sus cálculos en display math.
            bloque = []
            # Título del menor en texto simple (no mezclar con matrices)
            titulo_menor = r"\textbf{Menor } $M_{%d%d}$" % (i+1, j+1)
            bloque.append(titulo_menor)
            # Mostrar la matriz M_{ij} en display math
            bloque.append(r"\[ %s \]" % matriz_a_latex_bmatrix(Mij))
            # Mostrar det(Mij) y Cij en un entorno aligned para que \\ funcione
            aligned = (
                r"\begin{aligned}"
                r"\det(M_{%d%d}) &= %s \\[4pt]"
                r"C_{%d%d} &= (-1)^{%d+%d}\det(M_{%d%d}) = %s"
                r"\end{aligned}"
            ) % (i+1, j+1, frac_to_latex(detMij), i+1, j+1, i+1, j+1, i+1, j+1, frac_to_latex(Cij))
            bloque.append(r"\[ %s \]" % aligned)

            # unir bloque con separación pequeña
            contenido_menores.append("\n".join(bloque))
            
    pasos.append(("Menores y Cofactores (cada M_{ij}, \det(M_{ij}) y C_{ij})",
                  NoEscape("\n\n".join(contenido_menores))))

    # Paso 4: Matriz de cofactores C (mostrar en display)
    pasos.append(("Matriz de cofactores C", NoEscape(r"\[ C \;=\; %s \]" % matriz_a_latex_bmatrix(cofactor_matrix))))

    # Paso 5: Adjunta = transpose(C)
    adj = transpose(cofactor_matrix)
    pasos.append(("Adjunta (adjugate)", NoEscape(r"\[ \operatorname{adj}(A) \;=\; C^{T} \;=\; %s \]" % matriz_a_latex_bmatrix(adj))))

    # Paso 6: Inversa = (1/det(A)) * adj
    inv = multiply_scalar(adj, Fraction(1, 1) / detA)
    pasos.append(("Fórmula de la inversa",
                  NoEscape(r"\[ A^{-1} \;=\; \frac{1}{\det(A)}\,\operatorname{adj}(A) \;=\; \frac{1}{%s}\,%s \]"
                           % (frac_to_latex(detA), matriz_a_latex_bmatrix(adj)))))
    pasos.append(("Matriz inversa (entradas explícitas)", NoEscape(r"\[ A^{-1} \;=\; %s \]" % matriz_a_latex_bmatrix(inv))))

    return detA, pasos, adj, inv

def generar_documento_inversa(nombre_archivo, pasos):
    """
    Genera el PDF mostrando los pasos (pasos es lista de (titulo, contenido LaTeX NoEscape)).
    Se asumió que 'contenido' ya contiene los entornos matemáticos adecuados.
    """
    doc = Document(documentclass="article", document_options=["12pt"])

    doc.preamble.append(NoEscape(r"\usepackage{amsmath}"))
    doc.preamble.append(NoEscape(r"\usepackage{amssymb}"))
    doc.preamble.append(NoEscape(r"\usepackage{geometry}"))
    doc.preamble.append(NoEscape(r"\geometry{margin=1in}"))

    with doc.create(Section("Cálculo de la inversa mediante cofactores y adjunta")):
        doc.append(NoEscape("Se muestra el procedimiento paso a paso. Cada paso presenta la operación y la matriz resultante o la expresión matemática en modo display."))
        for idx, (titulo, contenido) in enumerate(pasos):
            with doc.create(Subsection(f"Paso {idx+1}: {titulo}")):
                doc.append(contenido)

    doc.generate_pdf(nombre_archivo, clean_tex=False)
    print(f"Documento generado: {nombre_archivo}.pdf (y {nombre_archivo}.tex)")

def ejemplo_3x3():
    return [
        [2, 1, 3],
        [1, 0, 2],
        [3, 4, 1]
    ]

def main():
    A_raw = ejemplo_3x3()
    print("Usando la matriz de ejemplo (3x3):")
    for r in A_raw:
        print(r)

    # comprobar cuadrada
    n = len(A_raw)
    if any(len(r) != n for r in A_raw):
        print("La matriz debe ser cuadrada.")
        sys.exit(1)

    detA, pasos, adj, inv = calcular_inversa_pasoaPaso(A_raw)

    generar_documento_inversa("inversa_cofactores_corregido", pasos)

if __name__ == "__main__":
    main()
