import random

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

        matrizR = Matriz(self.filas, other.columnas)

        for i in range (len(self.matriz)):
            for j in range (len(other.matriz[0])):
                for k in range (len(other.matriz)):
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


    


