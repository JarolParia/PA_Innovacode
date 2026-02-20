import random
from validaciones import validarMatrizCuadrada, puedenMultiplicarse

class Matriz:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.matriz = [[0 for _ in range(columnas)] for _ in range(filas)]
    
    @classmethod
    def crearMatriz(cls):

        while True:
            try: 
                filas = int(input("Ingrese el número de filas: "))
                columnas = int(input("Ingrese el número de columnas: "))

                if filas <= 0 or columnas <= 0:
                    print("Los valores deben ser mayores que 0. Intente nuevamente")
                    continue

                break
            except ValueError:
                print("Entrada no valida, porfavor ingrese un número entero")

        return cls._crear_aleatoria(filas, columnas)

    @classmethod
    def _crear_aleatoria(cls,filas,columnas):
        obj = cls(filas, columnas)
        for i in range(filas):
            for j in range(columnas):
                obj.matriz[i][j]= random.randint(1,20)
        return obj
    @classmethod

    def crear_manual(cls):
        try:
            filas = int(input("Ingrese número de filas: "))
            columnas = int(input("Ingrese número de columnas: "))

            obj = cls(filas, columnas)

            for i in range(filas):
                for j in range(columnas):
                    valor = float(input(f"Valor [{i}][{j}]: "))
                    obj.matriz[i][j] = valor

            return obj

        except ValueError:
            print("Entrada inválida. Debe ingresar números.")
            return None

    def mostrarMatriz(self):
        for fila in self.matriz:
            print(fila)


    def operacionesEntreMatrices(self,other,operacion):
        if not isinstance(other, Matriz):
            raise TypeError("El objeto debe ser una matriz")
        
        if self.filas != other. filas or self.columnas != other.columnas:
            raise ValueError("Las matrices deben de tener el mismo tamaño")
        
        nueva_matriz = Matriz(self.filas, self.columnas)

        for i in range(self.filas):
            for j in range(self.columnas):
                nueva_matriz.matriz[i][j] = operacion(self.matriz[i][j], other.matriz[i][j])

        return nueva_matriz
    


    def sumaMatrices(self,other):
        return self.operacionesEntreMatrices(other,lambda a,b: a+b)

    def restaMatrices(self,other):
        return self.operacionesEntreMatrices(other,lambda a,b: a-b)
    
    def divisionMatrices(self,other):
        return self.operacionesEntreMatrices(other,lambda a,b: a/b)
    
    def multiplicacionMatricesHadaman(self,other):
        return self.operacionesEntreMatrices(other,lambda a,b: a*b)
    
    def multiplicacionMatrices(self, other):

        if puedenMultiplicarse(self.columnas, other.filas) == False:
            raise ValueError("Las columnas de la matriz A deben coincidir con las filas de la matriz B")

        matrizR = Matriz(self.filas, other.columnas)

        for i in range (self.filas):
            for j in range (other.columnas):
                for k in range (self.columnas):
                    matrizR.matriz[i][j] += self.matriz[i][k]*other.matriz[k][j]

        return matrizR
    

    def operacionesEscalares(self,k,operacion):

        nueva_matriz = Matriz(self.filas, self.columnas)

        for i in range(self.filas):
            for j in range(self.columnas):
                nueva_matriz.matriz[i][j] = operacion(self.matriz[i][j], k)

        return nueva_matriz
    
    def sumaEscalar(self,k):
        return self.operacionesEscalares(k, lambda a,k:a+k)
    
    def restaEscalar(self,k):
        return self.operacionesEscalares(k, lambda a,k:a-k)
    
    def multiplicacionEscalar(self,k):
        return self.operacionesEscalares(k, lambda a,k:a*k)
    
    def divisionEscalar(self,k):
        return self.operacionesEscalares(k, lambda a,k:a/k )

    def determinante(self):
        validarMatrizCuadrada(self.filas,self.columnas)
        # Caso base: matriz 1x1
        if self.filas == 1:
            return self.matriz[0][0]
        # Caso base: matriz 2x2
        if self.filas == 2:
            return (self.matriz[0][0] * self.matriz[1][1]
                    - self.matriz[0][1] * self.matriz[1][0])
        # Caso recursivo
        det = 0
        for col in range(self.columnas):
            submatriz = [
                [self.matriz[i][j] for j in range(self.columnas) if j != col]
                for i in range(1, self.filas)
            ]

            sub = Matriz(self.filas - 1, self.columnas - 1)
            sub.matriz = submatriz

            det += ((-1) ** col) * self.matriz[0][col] * sub.determinante()

        return det

    def matrizAdjunta(self):
        validarMatrizCuadrada(self.filas,self.columnas)

        n = self.filas
        cofactores = Matriz(n, n)

        for i in range(n):
            for j in range(n):

                submatriz = [
                    [self.matriz[f][c] for c in range(n) if c != j]
                    for f in range(n) if f != i
                ]

                sub = Matriz(n - 1, n - 1)
                sub.matriz = submatriz

                cofactores.matriz[i][j] = ((-1) ** (i + j)) * sub.determinante()

        adjunta = Matriz(n, n)
        for i in range(n):
            for j in range(n):
                adjunta.matriz[j][i] = cofactores.matriz[i][j]

        return adjunta

    def inversa(self):
        validarMatrizCuadrada(self.filas,self.columnas)

        det = self.determinante()

        if det == 0:
            raise ValueError("La matriz no tiene inversa (determinante = 0)")

        adjunta = self.matrizAdjunta()

        inversa = adjunta.multiplicacionEscalar(1 / det)

        return inversa

    def traza(self):
        validarMatrizCuadrada(self.filas,self.columnas)

        suma = 0
        for i in range(self.filas):
            suma += self.matriz[i][i]

        return suma

    def transpuesta(self):
        matTranspuesta = Matriz(self.columnas,self.filas)
        for j in range(self.columnas):
            for i in range(self.filas):
                matTranspuesta.matriz[j][i] = self.matriz[i][j]
        
        return matTranspuesta    