def puedenMultiplicarse(columnasA,filasB):
    if columnasA == filasB:
        print("Las matrices son compatibles para su multiplicacion")
        return True
    else:
        print("Las columnas de la matriz A deben coincidir con las filas de la matriz B")
        return False
    
def validarMatrizCuadrada(filas,columnas):
    if columnas != filas:
        raise ValueError("La matriz debe ser cuadrada")
