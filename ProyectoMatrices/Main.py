from Matriz import Matriz ##Importamos la clase de matriz para poder usarla en el main, no es necesario importar en matriz al main
from validaciones import puedenMultiplicarse ##Importamos la funcion de validacion para poder usarla en el main



def crear_matriz(nombre="A", matriz_actual=None):

    # Si ya existe una matriz, preguntar si quiere reutilizarla
    if matriz_actual is not None:
        print(f"\nYa existe la matriz {nombre}:")
        matriz_actual.mostrarMatriz()
        usar = input(f"¿Desea usar esta misma matriz {nombre}? (s/n): ").strip().lower()

        if usar == "s":
            return matriz_actual
        # Si dice que no, continúa para crear una nueva

    while True:
        print(f"\nCreación de la matriz {nombre}")
        print("1. Manual")
        print("2. Aleatoria")
        print("0. Volver")

        opcion = input("Opción: ").strip()

        match opcion:
            case "1":
                matriz = Matriz.crear_manual()
            case "2":
                matriz = Matriz.crearMatriz()
            case "0":
                return matriz_actual  # conserva la anterior
            case _:
                print("Opción inválida")
                continue

        if matriz is not None:
            print(f"\nMatriz {nombre} creada:")
            matriz.mostrarMatriz()
            return matriz


def menu_unitaria():
    print("\nOPERACIONES UNITARIAS / ESCALARES")
    print("1. Suma escalar")
    print("2. Resta escalar")
    print("3. Multiplicación escalar")
    print("4. División escalar")
    print("5. Determinante")
    print("6. Matriz adjunta")
    print("7. Inversa")
    print("8. Traza")
    print("9. Transpuesta")
    print("0. Volver")


def menu_binaria():
    print("\nOPERACIONES BINARIAS")
    print("1. Suma")
    print("2. Resta")
    print("3. División")
    print("4. Multiplicación Hadamard")
    print("5. Producto matricial")
    print("0. Volver")


def main():

    A = None
    B = None

    while True:
        print("\n===== CALCULADORA DE MATRICES =====")
        print("1. Operaciones unitarias / escalares")
        print("2. Operaciones binarias")
        print("0. Salir")

        opcion = input("Seleccione una opción: ").strip()

        match opcion:

            # ================= UNITARIAS =================
            case "1":
                A = crear_matriz("A", A)
                if A is None:
                    print("No hay matriz A disponible.")
                    continue

                while True:
                    menu_unitaria()
                    op = input("Seleccione operación: ").strip()

                    try:
                        print("\nMatriz A antes de la operación:")
                        A.mostrarMatriz()

                        match op:
                            case "1":
                                k = float(input("Escalar: "))
                                R = A.sumaEscalar(k)
                                print("\nResultado A +", k)
                                R.mostrarMatriz()

                            case "2":
                                k = float(input("Escalar: "))
                                R = A.restaEscalar(k)
                                print("\nResultado A -", k)
                                R.mostrarMatriz()

                            case "3":
                                k = float(input("Escalar: "))
                                R = A.multiplicacionEscalar(k)
                                print("\nResultado A *", k)
                                R.mostrarMatriz()

                            case "4":
                                k = float(input("Escalar: "))
                                R = A.divisionEscalar(k)
                                print("\nResultado A /", k)
                                R.mostrarMatriz()

                            case "5":
                                print("\nDeterminante:", A.determinante())

                            case "6":
                                R = A.matrizAdjunta()
                                print("\nMatriz Adjunta:")
                                R.mostrarMatriz()

                            case "7":
                                R = A.inversa()
                                print("\nMatriz Inversa:")
                                R.mostrarMatriz()

                            case "8":
                                print("\nTraza:", A.traza())

                            case "9":
                                R = A.transpuesta()
                                print("\nMatriz Transpuesta:")
                                R.mostrarMatriz()

                            case "0":
                                break

                            case _:
                                print("Opción inválida")

                    except Exception as e:
                        print("Error:", e)

            # ================= BINARIAS =================
            case "2":
                A = crear_matriz("A", A)
                if A is None:
                    print("No hay matriz A disponible.")
                    continue

                B = crear_matriz("B", B)
                if B is None:
                    print("No hay matriz B disponible.")
                    continue

                while True:
                    menu_binaria()
                    op = input("Seleccione operación: ").strip()

                    try:
                        print("\nMatriz A antes de la operación:")
                        A.mostrarMatriz()
                        print("\nMatriz B antes de la operación:")
                        B.mostrarMatriz()

                        match op:
                            case "1":
                                R = A.sumaMatrices(B)
                                print("\nResultado A + B:")
                                R.mostrarMatriz()

                            case "2":
                                R = A.restaMatrices(B)
                                print("\nResultado A - B:")
                                R.mostrarMatriz()

                            case "3":
                                R = A.divisionMatrices(B)
                                print("\nResultado A / B:")
                                R.mostrarMatriz()

                            case "4":
                                R = A.multiplicacionMatricesHadaman(B)
                                print("\nResultado Hadamard:")
                                R.mostrarMatriz()

                            case "5":
                                if not puedenMultiplicarse(A.columnas, B.filas):
                                    continue
                                R = A.multiplicacionMatrices(B)
                                print("\nResultado Producto Matricial:")
                                R.mostrarMatriz()

                            case "0":
                                break

                            case _:
                                print("Opción inválida")

                    except Exception as e:
                        print("Error:", e)

            case "0":
                print("Programa finalizado")
                break

            case _:
                print("Opción inválida")


if __name__ == "__main__":
    main()