from . import env
import json
import csv
import pickle
from concurrent.futures import ThreadPoolExecutor
import threading

# ThreadPoolExecutor global para toda la clase
executor = ThreadPoolExecutor(max_workers=2)

try:
    from .core import NeuralNetwork
except ImportError:
    from .core_py import NeuralNetwork


class Inputs:
    neuralNetwork = NeuralNetwork()

    # ------------------------------
    # Internal: run a function in executor
    # ------------------------------
    def run_async(self, fn, *args, **kwargs):
        """
        Ejecuta la función `fn` en un thread del pool
        y devuelve un Future que puedes consultar si quieres.
        """

        def wrapper():
            try:
                fn(*args, **kwargs)
                # ejecutar entrenamiento al final
                self.neuralNetwork.start()
            except Exception as e:
                print(f"[ERROR] Error en tarea asincrónica {fn.__name__}: {e}")
                raise

        return executor.submit(wrapper)

    # ------------------------------
    # CONFIG FILES
    # ------------------------------
    def readConfigurationFile(self, fileName="config"):
        with open(fileName, 'r') as file:
            env.geneRange = float(file.readline())
            env.populationSizeInt = int(file.readline())
            env.numMaxGenerations = int(file.readline())
            env.allowedError = float(file.readline())
            env.mutationProbability = float(file.readline())

    def readJSONConfigurationFile(self, fileName="config.json"):
        with open(fileName, 'r') as f:
            config = json.load(f)

        env.geneRange = float(config['geneRange'])
        env.populationSizeInt = int(config['populationSize'])
        env.numMaxGenerations = int(config['numMaxGenerations'])
        env.allowedError = float(config['allowedError'])
        env.mutationProbability = float(config['mutationProbability'])

    def readCSVConfigurationFile(self, fileName="config.csv"):
        with open(fileName, 'r', encoding='utf-8') as f:
            rows = list(csv.reader(f))

        for row in rows[1:]:
            key, value = row
            if key == 'geneRange':
                env.geneRange = float(value)
            elif key == 'populationSize':
                env.populationSizeInt = int(value)
            elif key == 'numMaxGenerations':
                env.numMaxGenerations = int(value)
            elif key == 'allowedError':
                env.allowedError = float(value)
            elif key == 'mutationProbability':
                env.mutationProbability = float(value)

    def readPKLConfigurationFile(self, fileName="config.pkl"):
        with open(fileName, "rb") as f:
            config = pickle.load(f)

        env.geneRange = float(config['geneRange'])
        env.populationSizeInt = int(config['populationSize'])
        env.numMaxGenerations = int(config['numMaxGenerations'])
        env.allowedError = float(config['allowedError'])
        env.mutationProbability = float(config['mutationProbability'])

    # ------------------------------
    # TRAINING FILES
    # ------------------------------
    def readTrainingFile(self, fileName="trainingData"):
        with open(fileName, 'r') as file:
            # network layers
            data = list(map(int, file.readline().split()))
            env.networkLayerNeural = data
            env.inputsNumber = data[0]
            env.outputsNumber = data[-1]

            env.patternsNumber = int(file.readline())
            env.patternsInputArrangement.clear()
            env.patternsOutputArrangement.clear()

            env.flag = False

            # patterns
            for _ in range(env.patternsNumber):
                row = list(map(float, file.readline().split()))
                idx = 0
                # Inputs
                for _ in range(env.inputsNumber):
                    val = row[idx]
                    if val < 0:
                        env.flag = True
                    env.patternsInputArrangement.append(val)
                    idx += 1

                # Outputs
                for _ in range(env.outputsNumber):
                    val = row[idx]
                    if val < 0:
                        env.flag = True
                    env.patternsOutputArrangement.append(val)
                    idx += 1

    def readJSONTrainingFile(self, fileName="training.json"):
        with open(fileName, 'r', encoding="utf-8") as f:
            data = json.load(f)

        env.networkLayerNeural = data['networkLayerNeural']
        env.inputsNumber = env.networkLayerNeural[0]
        env.outputsNumber = env.networkLayerNeural[-1]

        env.patternsNumber = data['patternsNumber']

        env.patternsInputArrangement.clear()
        env.patternsOutputArrangement.clear()
        env.flag = False

        for pattern in data['patterns']:
            for val in pattern["inputs"]:
                if val < 0:
                    env.flag = True
                env.patternsInputArrangement.append(val)

            for val in pattern["outputs"]:
                if val < 0:
                    env.flag = True
                env.patternsOutputArrangement.append(val)

    def readCSVTrainingFile(self, fileName="training.csv"):
        with open(fileName, 'r', encoding="utf-8") as f:
            rows = list(csv.reader(f))

        env.networkLayerNeural = [int(x) for x in rows[1]]
        env.inputsNumber = env.networkLayerNeural[0]
        env.outputsNumber = env.networkLayerNeural[-1]

        env.patternsNumber = int(rows[3][0])

        env.patternsInputArrangement.clear()
        env.patternsOutputArrangement.clear()
        env.flag = False

        for row in rows[5:]:
            row = list(map(float, row))

            for val in row[:env.inputsNumber]:
                if val < 0:
                    env.flag = True
                env.patternsInputArrangement.append(val)

            for val in row[env.inputsNumber:]:
                if val < 0:
                    env.flag = True
                env.patternsOutputArrangement.append(val)

    def readPKLTrainingFile(self, fileName="training.pkl"):
        with open(fileName, 'rb') as f:
            data = pickle.load(f)

        env.networkLayerNeural = data['networkLayerNeural']
        env.inputsNumber = env.networkLayerNeural[0]
        env.outputsNumber = env.networkLayerNeural[-1]

        env.patternsNumber = data["patternsNumber"]

        env.patternsInputArrangement.clear()
        env.patternsOutputArrangement.clear()
        env.flag = False

        for pattern in data["patterns"]:
            for val in pattern["inputs"]:
                if val < 0:
                    env.flag = True
                env.patternsInputArrangement.append(val)

            for val in pattern["outputs"]:
                if val < 0:
                    env.flag = True
                env.patternsOutputArrangement.append(val)

    # ------------------------------
    # PUBLIC ASYNC METHODS
    # ------------------------------

    def readTrainingFileAsync(self, fileName="trainingData"):
        return self.run_async(self.readTrainingFile, fileName)

    def readJSONTrainingFileAsync(self, fileName="training.json"):
        return self.run_async(self.readJSONTrainingFile, fileName)

    def readCSVTrainingFileAsync(self, fileName="training.csv"):
        return self.run_async(self.readCSVTrainingFile, fileName)

    def readPKLTrainingFileAsync(self, fileName="training.pkl"):
        return self.run_async(self.readPKLTrainingFile, fileName)

    def readConfigurationFileAsync(self, fileName="config"):
        return self.run_async(self.readConfigurationFile, fileName)

    def readJSONConfigurationFileAsync(self, fileName="config.json"):
        return self.run_async(self.readJSONConfigurationFile, fileName)

    def readCSVConfigurationFileAsync(self, fileName="config.csv"):
        return self.run_async(self.readCSVConfigurationFile, fileName)

    def readPKLConfigurationFileAsync(self, fileName="config.pkl"):
        return self.run_async(self.readPKLConfigurationFile, fileName)

    # ------------------------------
    # MANUAL SET DATA (sync)
    # ------------------------------
    def setData(self, geneRange, populationSize, numMaxGenerations, allowedError,
                mutationProbability, networkLayers, patternsInput, patternsOutput):

        env.geneRange = geneRange
        env.populationSizeInt = populationSize
        env.numMaxGenerations = numMaxGenerations
        env.allowedError = allowedError
        env.mutationProbability = mutationProbability

        env.networkLayerNeural = networkLayers
        env.inputsNumber = networkLayers[0]
        env.outputsNumber = networkLayers[-1]

        env.patternsNumber = len(patternsInput) // env.inputsNumber
        env.patternsInputArrangement = patternsInput.copy()
        env.patternsOutputArrangement = patternsOutput.copy()

        env.flag = any(v < 0 for v in patternsInput + patternsOutput)

        self.neuralNetwork.start()

    def setGeneRange(self, geneRange):
        env.geneRange = geneRange

    def setPopulationSize(self, populationSize):
        env.populationSizeInt = populationSize

    def setNumMaxGenerations(self, numMaxGenerations):
        env.numMaxGenerations = numMaxGenerations

    def setAllowedError(self, allowedError):
        env.allowedError = allowedError

    def setMutationProbability(self, mutationProbability):
        env.mutationProbability = mutationProbability

    def setNetworkLayers(self, networkLayers):
        env.networkLayerNeural = networkLayers
        env.inputsNumber = networkLayers[0]
        env.outputsNumber = networkLayers[-1]

    def setPatternsInput(self, patternsInput):
        env.patternsInputArrangement = patternsInput

    def setPatternsOutput(self, patternsOutput):
        env.patternsOutputArrangement = patternsOutput

    def runNeuralNetwork(self):
        return self.neuralNetwork.start()