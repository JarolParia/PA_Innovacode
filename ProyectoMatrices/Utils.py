from Matriz import Matriz

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

