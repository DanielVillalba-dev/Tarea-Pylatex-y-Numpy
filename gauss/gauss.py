from pylatex import Document, Section, Subsection, NoEscape
from fractions import Fraction

def ejemplo_4x4():
    return [
        [Fraction(1),  Fraction(-2), Fraction(-1), Fraction(3)],
        [Fraction(-1), Fraction(3),  Fraction(-2), Fraction(-2)],
        [Fraction(2),  Fraction(0),  Fraction(1),  Fraction(1)],
        [Fraction(1),  Fraction(-2), Fraction(2),  Fraction(3)]
    ]

def copiar_matriz(A):
    # copia profunda segura para snapshots
    return [row[:] for row in A]

def matriz_a_latex(A):
    lines = []
    for row in A:
        elems = []
        for x in row:
            if isinstance(x, Fraction):
                if x.denominator == 1:
                    elems.append(str(x.numerator))
                else:
                    elems.append(r"\frac{%d}{%d}" % (x.numerator, x.denominator))
            else:
                elems.append(str(x))
        lines.append(" & ".join(elems))
    body = r" \\ ".join(lines)
    return r"\begin{bmatrix}" + body + r"\end{bmatrix}"

def gauss_con_registro(A_orig):
    """
    Hace la eliminación de Gauss sobre una copia de A_orig.
    Devuelve:
      - det (Fraction o 0 si singular)
      - pasos: lista de tuplas (descripcion_str, snapshot_matriz)
    """
    A = copiar_matriz(A_orig)
    n = len(A)
    pasos = []

    # paso inicial: matriz original
    pasos.append(("Matriz inicial", copiar_matriz(A)))

    intercambios = 0

    for k in range(n):
        # 1) Seleccionar/asegurar pivote en A[k][k]
        if A[k][k] == 0:
            # buscar fila para intercambiar
            fila_pivote = None
            for i in range(k+1, n):
                if A[i][k] != 0:
                    fila_pivote = i
                    break
            if fila_pivote is not None:
                A[k], A[fila_pivote] = A[fila_pivote], A[k]
                intercambios += 1
                pasos.append((f"Intercambio: F{k+1} ↔ F{fila_pivote+1} (para tener pivote no cero)", copiar_matriz(A)))
            else:
                pasos.append((f"No existe pivote no cero en columna {k+1}. Determinante = 0", copiar_matriz(A)))
                return Fraction(0), pasos

        # ahora A[k][k] es el pivote (no cero)
        pivote = A[k][k]

        # 2) Eliminar debajo del pivote (filas i = k+1 .. n-1)
        for i in range(k+1, n):
            if A[i][k] == 0:
                continue
            factor = Fraction(A[i][k], pivote)
            # actualizar fila i desde la columna k en adelante
            for j in range(k, n):
                A[i][j] = A[i][j] - factor * A[k][j]
            # registrar operación y snapshot
            pasos.append((f"Operación: F{i+1} ← F{i+1} - ({factor})·F{k+1}", copiar_matriz(A)))

    # al final A es triangular superior
    # determinante = (-1)^{intercambios} * producto diagonal
    producto = Fraction(1)
    for i in range(n):
        producto *= A[i][i]
    if intercambios % 2 != 0:
        producto = -producto

    pasos.append((f"Matriz triangular superior final (producto diagonal = {producto if intercambios%2==0 else -producto} con {intercambios} intercambios)", copiar_matriz(A)))
    pasos.append((f"Determinante = {producto}", copiar_matriz(A)))

    return producto, pasos

def generar_documento(nombre_archivo, pasos):

    doc = Document(documentclass="article", document_options=["12pt"])
    doc.preamble.append(NoEscape(r"\usepackage{amsmath}"))
    doc.preamble.append(NoEscape(r"\usepackage{geometry}"))
    doc.preamble.append(NoEscape(r"\geometry{margin=1in}"))

    with doc.create(Section("Cálculo del determinante por eliminación de Gauss")):
        doc.append(NoEscape("A continuación se documenta paso a paso el procedimiento. Para cada paso se indica la operación realizada y la matriz resultante."))

        for idx, (desc, mat) in enumerate(pasos):
            safe_desc = desc.replace("_", r"\_")
            with doc.create(Subsection(f"Paso {idx+1}: {safe_desc}")):
                latex_mat = matriz_a_latex(mat)
                doc.append(NoEscape(r"$$ %s $$" % latex_mat))

    doc.generate_pdf(nombre_archivo, clean_tex=False)

def main():
    A = ejemplo_4x4()

    det, pasos = gauss_con_registro(A)

    print("Matriz original (4x4):")
    for row in A:
        print([str(x) for x in row])
    print()
    # mostrar último paso en consola (determinante)
    print(pasos[-1][0])

    generar_documento("determinante_gauss_4x4", pasos)

if __name__ == "__main__":
    main()
