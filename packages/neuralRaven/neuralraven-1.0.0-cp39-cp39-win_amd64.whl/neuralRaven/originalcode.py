import cProfile
import pstats
import re
import numpy as np
import random
import math
import time

class rnaVB():
    nos = np.array([2, 2, 1])
    nCapas = len(nos)
    ne = nos[0]
    ns = nos[nCapas - 1]
    rangoPesos = 10
    probMut = 0.25
    errorPermitido = 0.0102
    numMaxGeneraciones = 1000
    nPat = 4
    intTamPob = 100;
    ntn = 0
    intnPesos = 0
    for i in range(0, nCapas - 1):
        intnPesos += (nos[i] * nos[i + 1] + nos[i + 1])
    for i in range(0, nCapas):
        ntn += nos[i]
    w = np.empty((intTamPob, intnPesos))
    wnuevo = np.empty((intTamPob, intnPesos))
    errorCuad = np.empty(intTamPob)
    complementoErrorCuad = np.empty(intTamPob)
    sumaComplementoErrorCuad = np.empty(intTamPob)
    xp = np.empty((nPat, ne))
    y = np.empty(ntn)
    errorPat = np.empty(nPat)
    d = np.empty((nPat, ns))
    neta = np.empty(ntn)
    errorMinimo = 0
    errorMaximo = 0
    monoSolucion = -1
    monoConMinError = 0
    sumaErrorPob = 0
    fracasos = 0
    exitos = 0

    def algoritmoGenetico(self):
        # entradas
        self.xp[0][0] = 0.0
        self.xp[0][1] = 0.0
        self.xp[1][0] = 1.0
        self.xp[1][1] = 0.0
        self.xp[2][0] = 0.0
        self.xp[2][1] = 1.0
        self.xp[3][0] = 1.0
        self.xp[3][1] = 1.0
        # salidas
        self.d[0][0] = 0.0
        self.d[1][0] = 1.0
        self.d[2][0] = 1.0
        self.d[3][0] = 0.0
        self.generarPoblacionInicial(self.intTamPob, self.intnPesos, self.rangoPesos)
        numGeneracion = 0
        self.monoSolucion = -1
        while (self.monoSolucion == -1 and numGeneracion < self.numMaxGeneraciones):
            self.sumaErrorPob = 0
            self.errorMaximo = 0
            self.errorMinimo = 50.5
            self.monoConMinError = 0
            self.evaluaPoblacion()
            if (self.monoSolucion != -1):
                break
            self.errorMaximo += 0.5
            self.seleccion()
            self.mutar()
            self.nuevaPoblacionConElitismo()
            numGeneracion += 1
        if (numGeneracion == self.numMaxGeneraciones):
            self.fracasos += 1
        print("Generacion final", numGeneracion)
        print("Error final", self.errorMinimo)
        print("mono", self.monoSolucion)

    def generarPoblacionInicial(self, nMonos, nPesos, rango):
        for i in range(0, nMonos):
            for j in range(0, nPesos):
                self.w[i][j] = self.inicializaMono(rango)

    def inicializaMono(self, r):
        return r * self.aleatorio()

    def aleatorio(self):
        dblNumx = random.random()
        if (dblNumx < 0.5):
            dblSigno = -1.0
        else:
            dblSigno = 1.0
        return dblSigno * random.random()

    def evaluaPoblacion(self):
        for i in range(0, self.intTamPob):
            self.evaluaMono(i)
            self.sumaErrorPob += self.errorCuad[i]
            if (self.errorMaximo < self.errorCuad[i]):
                self.errorMaximo = self.errorCuad[i]
            if (self.errorMinimo > self.errorCuad[i]):
                self.errorMinimo = self.errorCuad[i]
                self.monoConMinError = i
            if (self.errorCuad[i] < self.errorPermitido):
                self.monoSolucion = i
                self.exitos += 1
                #print("Solucion con mono", self.monoSolucion,"con error de", self.errorCuad[i])
                #self.imprimeMono(self.monoSolucion)
                #self.diagnostico(self.monoSolucion)
                break

    def evaluaMono(self, nMono):
        for numpatron in range(0, self.nPat):
            nCapa = 0
            nPeso = 0
            sNeurs = self.ne
            while (nCapa < self.nCapas):
                if (nCapa == 0):
                    for nneur in range(0, self.ne):
                        self.neta[nneur] = self.xp[numpatron][nneur]
                        self.y[nneur] = self.neta[nneur]
                    nCapa += 1
                else:
                    for nneur in range(sNeurs, (sNeurs + self.nos[nCapa])):
                        sumaNeta = 0
                        e = (sNeurs - self.nos[nCapa - 1])
                        while (e < sNeurs):
                            sumaNeta = sumaNeta + self.w[nMono][nPeso] * self.y[e]
                            e += 1
                            nPeso += 1
                        self.neta[nneur] = sumaNeta + -1.0 * self.w[nMono][nPeso]
                        self.y[nneur] = self.squash(self.neta[nneur])
                        nPeso += 1
                    sNeurs += self.nos[nCapa]
                    nCapa += 1
            sumaError = 0
            elemS = 0
            sNeurs -= self.nos[self.nCapas - 1]
            for nneur in range(sNeurs, self.ntn):
                sumaError = sumaError + ((self.d[numpatron][elemS] - self.y[nneur]) * (self.d[numpatron][elemS] - self.y[nneur]))
                elemS += 1
            self.errorPat[numpatron] = sumaError
        sumaerrorCuad = 0
        for i in range(0, self.nPat):
            sumaerrorCuad = sumaerrorCuad + self.errorPat[i]
        self.errorCuad[nMono] = sumaerrorCuad

    def squash(self, neta):
        if (neta < -50.0):
            return 0.0
        else:
            if (neta > 50.0):
                return 1.0
            else:
                return 1 / (1 + math.exp(-neta))
                # return neta / math.sqrt(1 + neta * neta)

    def seleccion(self):
        sumaComplementos = 0
        for i in range(0, self.intTamPob):
            self.complementoErrorCuad[i] = self.errorMaximo - self.errorCuad[i]
            sumaComplementos = sumaComplementos + self.complementoErrorCuad[i]
        suma = 0
        for i in range(0, self.intTamPob):
            suma = suma + self.complementoErrorCuad[i]
            self.sumaComplementoErrorCuad[i] = suma / sumaComplementos
        for nMono in range(0, self.intTamPob, 2):
            r = random.random()
            i = 0
            while (r > self.sumaComplementoErrorCuad[i] and i < self.intTamPob):
                i += 1
            monoSeleccionado1 = i
            r = random.random()
            i = 0
            while (r > self.sumaComplementoErrorCuad[i] and i < self.intTamPob):
                i += 1
            monoSeleccionado2 = i
            self.cruza(monoSeleccionado1, monoSeleccionado2, nMono)

    def cruza(self, mono1, mono2, monoNuevo):
        r = random.random()
        numPesoAleat = int(1 + (self.intnPesos - 1) * r)
        for i in range(0, numPesoAleat):
            self.wnuevo[monoNuevo][i] = self.w[mono1][i]
            self.wnuevo[monoNuevo + 1][i] = self.w[mono2][i]
        for i in range(numPesoAleat, self.intnPesos):
            self.wnuevo[monoNuevo][i] = self.w[mono2][i]
            self.wnuevo[monoNuevo + 1][i] = self.w[mono1][i]

    def mutar(self):
        for nMono in range(0, self.intTamPob):
            r = random.random()
            if (r < self.probMut):
                genMuta = int(random.random() * self.intnPesos)
                self.wnuevo[nMono][genMuta] = (self.w[nMono][genMuta] + self.rangoPesos * self.aleatorio()) / 2.0

    def nuevaPoblacionConElitismo(self):
        for i in range(0, self.intTamPob):
            if (i != self.monoConMinError):
                for j in range(0, self.intnPesos):
                    self.w[i][j] = self.wnuevo[i][j]

    def imprimeMono(self, nMono):
        print(self.w[nMono])

    def diagnostico(self, nMono):
        for numpatron in range(0, self.nPat):
            nCapa = 0
            nPeso = 0
            sNeurs = self.ne
            while (nCapa < self.nCapas):
                if (nCapa == 0):
                    for nneur in range(0, self.ne):
                        self.neta[nneur] = self.xp[numpatron][nneur]
                        self.y[nneur] = self.neta[nneur]
                    nCapa += 1
                else:
                    for nneur in range(sNeurs, (sNeurs + self.nos[nCapa])):
                        sumaNeta = 0
                        e = (sNeurs - self.nos[nCapa - 1])
                        while (e < sNeurs):
                            sumaNeta = sumaNeta + self.w[nMono][nPeso] * self.y[e]
                            e += 1
                            nPeso += 1
                        self.neta[nneur] = sumaNeta + -1.0 * self.w[nMono][nPeso]
                        self.y[nneur] = self.squash(self.neta[nneur])
                        if (nCapa == self.nCapas - 1):
                            print("Y salida", self.y[nneur])
                        nPeso += 1
                    sNeurs += self.nos[nCapa]
                    nCapa += 1

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("DOLPHIN RNA")
    totalSum = 0
    repeticiones = 3
    rna = rnaVB()
    with cProfile.Profile() as profile:
        for i in range(0,repeticiones):
            tiempoInicio = time.time()
            rna.algoritmoGenetico()
            totalSum += (time.time() - tiempoInicio)
        print("En",repeticiones,"intentos de entrenamiento")
        print("exitos en entrenamiento",rna.exitos)
        print("fracasos en entrenamiento",rna.fracasos)
        print("tiempo total de entrenamiento",totalSum,"segundos")
    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.print_stats()
    results.dump_stats("results.prof")

