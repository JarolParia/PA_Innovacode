from Matriz import Matriz ##Importamos la clase de matriz para poder usarla en el main, no es necesario importar en matriz al main
from ProyectoMatrices.validaciones import puedenMultiplicarse ##Importamos la funcion de validacion para poder usarla en el main

def Main():
    A = Matriz.crearMatriz()
    B = Matriz.crearMatriz()
    A.mostrarMatriz()
    B.mostrarMatriz()
    C = A.sumaMatrices(B)
    k=2
    D=A.sumaEscalar(k)



    """print("Suma de A y B:")
    C.mostrarMatriz()
    print(f"Suma de A con el escalar {k}:")
    D.mostrarMatriz()
    print(f"resta de A con el escalar {k}:")
    A.restaEscalar(k).mostrarMatriz()
    print(f"Multiplicacion de A con el escalar {k}:")
    A.multiplicacionEscalar(k).mostrarMatriz()
    print(f"Division de A con el escalar {k}:")
    A.divisionEscalar(k).mostrarMatriz()"""
    

    if (puedenMultiplicarse(A.columnas,B.filas)):
        E = A.multiplicacionMatrices(B)
        print("Multiplicacion de A y B:")
        E.mostrarMatriz()



if __name__ == "__main__":
    Main()


