def puedenMultiplicarse(columnasA,filasB):
    return columnasA == filasB
    
def validarMatrizCuadrada(filas,columnas):
    if columnas != filas:
        raise ValueError("La matriz debe ser cuadrada")

def mostrar_estado(A=None, B=None):
    print("\n" + "-"*40)

    if A is not None:
        print("Matriz A:")
        A.mostrarMatriz()

    if B is not None:
        print("Matriz B:")
        B.mostrarMatriz()

    print("-"*40)