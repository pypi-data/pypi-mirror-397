# distutils: language = c++
# cython: boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False, nonecheck=False
import numpy as np
cimport numpy as np
import random
import math
import os
from libc.math cimport exp
from . import env
ctypedef np.float64_t data_type

# ---------------------------------------------------------------------
# Implementación robusta con memoryviews:
# - atributos que almacenan numpy arrays como `object`
# - dentro de funciones calientes: memoryviews tipadas `double[:]` / `double[:,:]`
# - todas las cdef locales al inicio de la función
# ---------------------------------------------------------------------

cdef inline double squash_c(double neta):
    """
    Sigmoide en C (usa libc.exp).
    """
    if neta < -50.0:
        return 0.0
    elif neta > 50.0:
        return 1.0
    else:
        return 1.0 / (1.0 + exp(-neta))


cdef class NeuralNetwork:
    # Atributos simples en C
    cdef int nLayers
    cdef int totalNeurons

    # Referencias a numpy arrays (objetos Python)
    cdef object patError_arr
    cdef object xp_arr
    cdef object d_arr
    cdef object y_arr
    cdef object neta_arr
    cdef object W_arr
    cdef object newW_arr
    cdef object complementQuadraticErrorSum_arr
    cdef object complementQuadraticError_arr

    def __cinit__(self):
        # inicializaciones
        self.nLayers = 0
        self.totalNeurons = 0

        # Intentar crear arrays basicos si env ya tiene valores (si no, quedan None)
        try:
            self.complementQuadraticErrorSum_arr = np.empty(env.populationSizeInt, dtype=np.float64)
            self.complementQuadraticError_arr = np.empty(env.populationSizeInt, dtype=np.float64)
        except Exception:
            self.complementQuadraticErrorSum_arr = None
            self.complementQuadraticError_arr = None

        try:
            self.patError_arr = np.empty(max(1, env.patternsNumber), dtype=np.float64)
        except Exception:
            self.patError_arr = None

        try:
            env.quadraticError = np.empty(env.populationSizeInt, dtype=np.float64)
        except Exception:
            env.quadraticError = None

        env.minError = 0.0
        env.maxError = 0.0
        env.ravenSolution = -1
        env.ravenConMinError = 0
        env.populationErrorSum = 0.0
        env.fails = 0
        env.success = 0

    def start(self):
        """
        Inicializa tamaños, arrays y carga patrones desde env.
        """
        cdef int i
        cdef int num_patterns, inputsN, outputsN

        # calcular capas y totales
        self.nLayers = len(env.networkLayerNeural)
        self.totalNeurons = sum(env.networkLayerNeural)
        num_patterns = env.patternsNumber
        inputsN = env.inputsNumber
        outputsN = env.outputsNumber

        # Inicializar intnWeight si es 0
        if env.intnWeight == 0:
            env.intnWeight = 0
            for i in range(self.nLayers - 1):
                env.intnWeight += env.networkLayerNeural[i] * env.networkLayerNeural[i + 1] + env.networkLayerNeural[i + 1]

        # Crear arrays numpy (guardamos referencias; dtype=float64 obligatorio)
        self.W_arr = np.empty((env.populationSizeInt, env.intnWeight), dtype=np.float64)
        self.newW_arr = np.empty((env.populationSizeInt, env.intnWeight), dtype=np.float64)

        self.xp_arr = np.empty((max(1, num_patterns), max(1, inputsN)), dtype=np.float64)
        self.d_arr = np.empty((max(1, num_patterns), max(1, outputsN)), dtype=np.float64)
        self.y_arr = np.empty(max(1, self.totalNeurons), dtype=np.float64)
        self.neta_arr = np.empty(max(1, self.totalNeurons), dtype=np.float64)
        self.patError_arr = np.empty(max(1, num_patterns), dtype=np.float64)

        # Cargar datos desde env.patternsInputArrangement y patternsOutputArrangement
        try:
            self.xp_arr = np.array(env.patternsInputArrangement, dtype=np.float64).reshape((num_patterns, inputsN))
        except Exception:
            self.xp_arr = np.zeros((num_patterns, inputsN), dtype=np.float64)

        try:
            self.d_arr = np.array(env.patternsOutputArrangement, dtype=np.float64).reshape((num_patterns, outputsN))
        except Exception:
            self.d_arr = np.zeros((num_patterns, outputsN), dtype=np.float64)

        # Lanzar algoritmo genético
        return self.geneticAlgorithm()

    cpdef void selection(self):
        """
        Selección por ruleta utilizando complementos del error.
        """
        cdef int i, nRaven, ravenChoosen1, ravenChoosen2
        cdef double complementSum = 0.0, r, ssum

        if self.complementQuadraticError_arr is None:
            self.complementQuadraticError_arr = np.empty(env.populationSizeInt, dtype=np.float64)
        if self.complementQuadraticErrorSum_arr is None:
            self.complementQuadraticErrorSum_arr = np.empty(env.populationSizeInt, dtype=np.float64)

        for i in range(env.populationSizeInt):
            self.complementQuadraticError_arr[i] = env.maxError - env.quadraticError[i]
            complementSum += self.complementQuadraticError_arr[i]

        ssum = 0.0
        for i in range(env.populationSizeInt):
            ssum += self.complementQuadraticError_arr[i]
            self.complementQuadraticErrorSum_arr[i] = ssum / complementSum if complementSum != 0.0 else 0.0

        for nRaven in range(0, env.populationSizeInt, 2):
            r = random.random()
            i = 0
            while i < env.populationSizeInt - 1 and r > self.complementQuadraticErrorSum_arr[i]:
                i += 1
            ravenChoosen1 = i

            r = random.random()
            i = 0
            while i < env.populationSizeInt - 1 and r > self.complementQuadraticErrorSum_arr[i]:
                i += 1
            ravenChoosen2 = i

            self.crossbreed(ravenChoosen1, ravenChoosen2, nRaven)

    def crossbreed(self, raven1, raven2, newRaven):
        cdef int i, numRandomSize
        cdef double r
        r = random.random()
        numRandomSize = int(1 + (env.intnWeight - 1) * r)
        for i in range(numRandomSize):
            self.newW_arr[newRaven][i] = self.W_arr[raven1][i]
            self.newW_arr[newRaven + 1][i] = self.W_arr[raven2][i]
        for i in range(numRandomSize, env.intnWeight):
            self.newW_arr[newRaven][i] = self.W_arr[raven2][i]
            self.newW_arr[newRaven + 1][i] = self.W_arr[raven1][i]

    def mutation(self):
        cdef int nRaven, mutationGen
        cdef double r
        for nRaven in range(env.populationSizeInt):
            r = random.random()
            if r < env.mutationProbability:
                mutationGen = int(random.random() * env.intnWeight)
                self.newW_arr[nRaven][mutationGen] = (self.W_arr[nRaven][mutationGen] + env.weightRange * self.randomized()) / 2.0

    def randomized(self):
        cdef double dblNumx, dblSign
        dblNumx = random.random()
        dblSign = -1.0 if dblNumx < 0.5 else 1.0
        return dblSign * random.random()

    def startRaven(self, double r):
        return r * self.randomized()

    cpdef void ravenEvaluate(self, int nRaven):
        """
        Evaluación de un individuo.
        Usamos memoryviews locales tipadas para acelerar acceso a arrays numpy.
        """
        # Declaraciones al inicio
        cdef int numPattern, nLayer, nWeight, sNeurons, nneuron, e, elemS
        cdef int layer_neurons, prev_layer_neurons
        cdef double netaSum, errorSum, diff, quadraticErrorSum
        cdef int patternsN = env.patternsNumber
        cdef int inputsN = env.inputsNumber
        cdef int i

        # Memoryviews locales (declaradas e inicializadas a None)
        cdef double[:, :] xp_mv = None
        cdef double[:, :] d_mv = None
        cdef double[:] y_mv = None
        cdef double[:] neta_mv = None
        cdef double[:] patError_mv = None
        cdef double[:, :] Wloc_mv = None

        # Intentar vincular memoryviews con numpy arrays (dtype float64 requerido)
        try:
            xp_mv = self.xp_arr
            d_mv = self.d_arr
            y_mv = self.y_arr
            neta_mv = self.neta_arr
            patError_mv = self.patError_arr
            Wloc_mv = self.W_arr
        except Exception:
            # Si algo sale mal, los memoryviews permanecerán en None y caeremos al acceso por numpy Python
            xp_mv = None
            d_mv = None
            y_mv = None
            neta_mv = None
            patError_mv = None
            Wloc_mv = None

        quadraticErrorSum = 0.0

        for numPattern in range(patternsN):
            nLayer = 0
            nWeight = 0
            sNeurons = inputsN

            # capa de entrada: copiar inputs
            if xp_mv is not None and neta_mv is not None and y_mv is not None:
                for nneuron in range(inputsN):
                    neta_mv[nneuron] = xp_mv[numPattern, nneuron]
                    y_mv[nneuron] = neta_mv[nneuron]
                nLayer = 1
            else:
                # fallback seguro si memoryview no disponible
                for nneuron in range(inputsN):
                    neta_mv[nneuron] = self.xp_arr[numPattern][nneuron]
                    y_mv[nneuron] = neta_mv[nneuron]
                nLayer = 1

            while nLayer < self.nLayers:
                layer_neurons = env.networkLayerNeural[nLayer]
                prev_layer_neurons = env.networkLayerNeural[nLayer - 1]

                for nneuron in range(sNeurons, sNeurons + layer_neurons):
                    netaSum = 0.0
                    e = sNeurons - prev_layer_neurons

                    while e < sNeurons:
                        if Wloc_mv is not None and y_mv is not None:
                            netaSum += Wloc_mv[nRaven, nWeight] * y_mv[e]
                        else:
                            netaSum += self.W_arr[nRaven][nWeight] * (y_mv[e] if y_mv is not None else self.y_arr[e])
                        e += 1
                        nWeight += 1

                    if Wloc_mv is not None:
                        neta_mv[nneuron] = netaSum + -1.0 * Wloc_mv[nRaven, nWeight]
                    else:
                        neta_mv[nneuron] = netaSum + -1.0 * self.W_arr[nRaven][nWeight]

                    # usar la version en C de la sigmoide para velocidad
                    y_mv[nneuron] = squash_c(neta_mv[nneuron])
                    nWeight += 1

                sNeurons += layer_neurons
                nLayer += 1

            errorSum = 0.0
            elemS = 0
            sNeurons -= env.networkLayerNeural[self.nLayers - 1]

            # calcular el error cuadrático para las salidas
            for nneuron in range(sNeurons, self.totalNeurons):
                if d_mv is not None and y_mv is not None:
                    diff = d_mv[numPattern, elemS] - y_mv[nneuron]
                else:
                    diff = self.d_arr[numPattern][elemS] - (y_mv[nneuron] if y_mv is not None else self.y_arr[nneuron])
                errorSum += diff * diff
                elemS += 1

            if patError_mv is not None:
                patError_mv[numPattern] = errorSum
            else:
                self.patError_arr[numPattern] = errorSum

            quadraticErrorSum += errorSum

        env.quadraticError[nRaven] = quadraticErrorSum

    def newPopulationWithElitims(self):
        cdef int i, j
        for i in range(env.populationSizeInt):
            if i != env.ravenConMinError:
                for j in range(env.intnWeight):
                    self.W_arr[i][j] = self.newW_arr[i][j]

    def populationEvaluate(self):
        """
        Evaluación secuencial de la población.
        Si se desea paralelizar, reescribir ravenEvaluate para que devuelva
        el resultado en lugar de escribir en env.
        """
        cdef int i
        env.populationErrorSum = 0.0
        env.maxError = 0.0
        env.minError = 50.5
        env.ravenConMinError = 0

        for i in range(env.populationSizeInt):
            self.ravenEvaluate(i)
            env.populationErrorSum += env.quadraticError[i]
            if env.maxError < env.quadraticError[i]:
                env.maxError = env.quadraticError[i]
            if env.minError > env.quadraticError[i]:
                env.minError = env.quadraticError[i]
                env.ravenConMinError = i
            if env.quadraticError[i] < env.allowedError:
                env.ravenSolution = i
                env.success += 1
                break

    def initialPopulationGenerator(self, nRavens, nWeights, Range):
        """
        Genera la población inicial de cuervos (individuos).
        Rango = env.weightRange.
        """
        cdef int i, j
        for i in range(nRavens):
            for j in range(nWeights):
                self.W_arr[i][j] = self.startRaven(Range)


    def geneticAlgorithm(self):
        cdef int generationNumber = 0
        self.initialPopulationGenerator(env.populationSizeInt, env.intnWeight, env.weightRange)
        env.ravenSolution = -1

        while env.ravenSolution == -1 and generationNumber < env.numMaxGenerations:
            env.populationErrorSum = 0.0
            env.maxError = 0.0
            env.minError = 50.5
            env.ravenConMinError = 0
            self.populationEvaluate()
            if env.ravenSolution != -1:
                break
            env.maxError += 0.5
            self.selection()
            self.mutation()
            self.newPopulationWithElitims()
            generationNumber += 1
        if generationNumber == env.numMaxGenerations:
            env.fails += 1

        if env.ravenSolution != -1:
            winner_index = env.ravenSolution  # Ganador real
        else:
            winner_index = env.ravenConMinError
        result = {
            "generation": generationNumber,
            "min_error": env.minError,
            "winner_index": winner_index,
            "weights": np.array(self.W_arr[winner_index], dtype=np.float64)
        }
        return result