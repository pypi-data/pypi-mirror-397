# core.py
import numpy as np
import random
import math
from . import env

class NeuralNetwork:
    def __init__(self):
        self.nLayers = 0
        self.totalNeurons = 0

        self.W = None
        self.newW = None
        self.xp = None
        self.y = None
        self.neta = None
        self.d = None
        self.patError = None
        self.complementQuadraticError = None
        self.complementQuadraticErrorSum = None

        self.complementQuadraticErrorSum = np.empty(env.populationSizeInt, dtype=np.float64)
        self.complementQuadraticError = np.empty(env.populationSizeInt, dtype=np.float64)
        self.patError = np.empty(env.patternsNumber, dtype=np.float64)

        env.quadraticError = np.empty(env.populationSizeInt, dtype=np.float64)
        env.minError = 0
        env.maxError = 0
        env.ravenSolution = -1
        env.ravenConMinError = 0
        env.populationErrorSum = 0
        env.fails = 0
        env.success = 0

    def start(self):
        self.nLayers = len(env.networkLayerNeural)
        self.totalNeurons = sum(env.networkLayerNeural)
        num_patterns = env.patternsNumber

        if env.intnWeight == 0:
            env.intnWeight = 0
            for i in range(self.nLayers - 1):
                env.intnWeight += env.networkLayerNeural[i] * env.networkLayerNeural[i + 1] + env.networkLayerNeural[i + 1]

        self.W = np.empty((env.populationSizeInt, env.intnWeight), dtype=np.float64)
        self.newW = np.empty((env.populationSizeInt, env.intnWeight), dtype=np.float64)
        self.xp = np.empty((num_patterns, env.inputsNumber), dtype=np.float64)
        self.d = np.empty((num_patterns, env.outputsNumber), dtype=np.float64)
        self.y = np.empty(self.totalNeurons, dtype=np.float64)
        self.neta = np.empty(self.totalNeurons, dtype=np.float64)
        self.patError = np.empty(num_patterns, dtype=np.float64)

        # Cargar datos
        self.xp = np.array(env.patternsInputArrangement).reshape(num_patterns, env.inputsNumber)
        self.d = np.array(env.patternsOutputArrangement).reshape(num_patterns, env.outputsNumber)

        return self.geneticAlgorithm()

    def selection(self):
        complementSum = 0.0
        for i in range(env.populationSizeInt):
            self.complementQuadraticError[i] = env.maxError - env.quadraticError[i]
            complementSum += self.complementQuadraticError[i]

        ssum = 0.0
        for i in range(env.populationSizeInt):
            ssum += self.complementQuadraticError[i]
            self.complementQuadraticErrorSum[i] = ssum / complementSum

        for nRaven in range(0, env.populationSizeInt, 2):
            r = random.random()
            i = 0
            while r > self.complementQuadraticErrorSum[i] and i < env.populationSizeInt - 1:
                i += 1
            ravenChoosen1 = i

            r = random.random()
            i = 0
            while r > self.complementQuadraticErrorSum[i] and i < env.populationSizeInt - 1:
                i += 1
            ravenChoosen2 = i

            self.crossbreed(ravenChoosen1, ravenChoosen2, nRaven)

    def crossbreed(self, raven1, raven2, newRaven):
        numRandomSize = int(1 + (env.intnWeight - 1) * random.random())
        for i in range(numRandomSize):
            self.newW[newRaven, i] = self.W[raven1, i]
            self.newW[newRaven + 1, i] = self.W[raven2, i]
        for i in range(numRandomSize, env.intnWeight):
            self.newW[newRaven, i] = self.W[raven2, i]
            self.newW[newRaven + 1, i] = self.W[raven1, i]

    def mutation(self):
        for nRaven in range(env.populationSizeInt):
            if random.random() < env.mutationProbability:
                mutationGen = int(random.random() * env.intnWeight)
                self.newW[nRaven, mutationGen] = (self.W[nRaven, mutationGen] + env.weightRange * self.randomized()) / 2.0

    def randomized(self):
        return (-1 if random.random() < 0.5 else 1) * random.random()

    def startRaven(self, r):
        return r * self.randomized()

    def initialPopulationGenerator(self, nRavens, nWeights, Range):
        for i in range(nRavens):
            for j in range(nWeights):
                self.W[i, j] = self.startRaven(Range)

    def squash(self, neta):
        if neta < -50.0:
            return 0.0
        elif neta > 50.0:
            return 1.0
        else:
            return 1 / (1 + math.exp(-neta))

    def ravenEvaluate(self, nRaven):
        quadraticErrorSum = 0.0
        for numPattern in range(env.patternsNumber):
            nLayer = 0
            nWeight = 0
            sNeurons = env.inputsNumber

            while nLayer < self.nLayers:
                if nLayer == 0:
                    for nneuron in range(env.inputsNumber):
                        self.neta[nneuron] = self.xp[numPattern][nneuron]
                        self.y[nneuron] = self.neta[nneuron]
                    nLayer += 1
                else:
                    for nneuron in range(sNeurons, sNeurons + env.networkLayerNeural[nLayer]):
                        netaSum = 0.0
                        e = sNeurons - env.networkLayerNeural[nLayer - 1]
                        while e < sNeurons:
                            netaSum += self.W[nRaven, nWeight] * self.y[e]
                            e += 1
                            nWeight += 1
                        self.neta[nneuron] = netaSum + -1.0 * self.W[nRaven, nWeight]
                        self.y[nneuron] = self.squash(self.neta[nneuron])
                        nWeight += 1
                    sNeurons += env.networkLayerNeural[nLayer]
                    nLayer += 1

            errorSum = 0.0
            elemS = 0
            sNeurons -= env.networkLayerNeural[self.nLayers - 1]
            for nneuron in range(sNeurons, self.totalNeurons):
                diff = self.d[numPattern][elemS] - self.y[nneuron]
                errorSum += diff * diff
                elemS += 1
            self.patError[numPattern] = errorSum
            quadraticErrorSum += self.patError[numPattern]

        env.quadraticError[nRaven] = quadraticErrorSum

    def newPopulationWithElitims(self):
        for i in range(env.populationSizeInt):
            if i != env.ravenConMinError:
                self.W[i, :] = self.newW[i, :]

    def populationEvaluate(self):
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

    def geneticAlgorithm(self):
        generationNumber = 0
        self.initialPopulationGenerator(env.populationSizeInt, env.intnWeight, env.weightRange)
        env.ravenSolution = -1

        while env.ravenSolution == -1 and generationNumber < env.numMaxGenerations:
            env.populationErrorSum = 0
            env.maxError = 0
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
            "weights": np.array(self.W[winner_index], dtype=np.float64)
        }
        return result