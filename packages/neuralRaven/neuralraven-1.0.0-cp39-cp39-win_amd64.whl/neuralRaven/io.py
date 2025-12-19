import os
from .inputs import Inputs
from . import env

class IO():
    inputs = Inputs()

    @classmethod
    def fromFiles(self, file_configuration_name, file_data_name):
        ext = os.path.splitext(file_configuration_name)[1].lower()
        ext2 = os.path.splitext(file_data_name)[1].lower()
        if ext == '.json':
            self.inputs.readJSONConfigurationFile(file_configuration_name)
        elif ext == '.csv':
            self.inputs.readCSVConfigurationFile(file_configuration_name)
        elif ext == '.pkl':
            self.inputs.readPickleConfigurationFile(file_configuration_name)
        else:
            self.inputs.readConfigurationFile(file_configuration_name)

        if ext2 == '.json':
            self.inputs.readJSONTrainigFile(file_data_name)
        elif ext2 == '.csv':
            self.inputs.readCSVTrainigFile(file_data_name)
        elif ext2 == '.pkl':
            self.inputs.readPickleTrainigFile(file_data_name)
        else:
            self.inputs.readTrainingFile(file_data_name)
        result = self.inputs.runNeuralNetwork()
        return result

    @classmethod
    def fromData(self, geneRange: float, populationSize: int, numMaxGenerations: int, allowedError: float, mutationProbability: float, networkLayers: list[int], patternsInput: list[float], patternsOutput: list[float]):
        self.inputs.setData(geneRange, populationSize, numMaxGenerations, allowedError, mutationProbability, networkLayers, patternsInput, patternsOutput)

    @classmethod
    def getRavenSolution(self):
        return env.W[env.apeSolution]

    @classmethod
    def getMinError(self):
        return env.minError

    @classmethod
    def getNumFails(self):
        return env.fails

    @classmethod
    def getNumSuccess(self):
        return env.success

    @classmethod
    def setGeneticRange(self, geneRange):
        self.inputs.setGeneRange(geneRange)

    @classmethod
    def setPopulationSize(self, populationSize):
        self.inputs.setPopulationSize(populationSize)

    @classmethod
    def setNumMaxGenerations(self, numMaxGenerations):
        self.inputs.setNumMaxGenerations(numMaxGenerations)

    @classmethod
    def setAllowedError(self, allowedError):
        self.inputs.setAllowedError(allowedError)

    @classmethod
    def setMutationProbability(self, mutationProbability):
        self.inputs.setMutationProbability(mutationProbability)

    @classmethod
    def setNetworkLayers(self, networkLayers):
        self.inputs.setNetworkLayers(networkLayers)

    @classmethod
    def setPatternsInput(self, patternsInput):
        self.inputs.setPatternsInput(patternsInput)

    @classmethod
    def setPatternsOutput(self, patternsOutput):
        self.inputs.setPatternsOutput(patternsOutput)

    @classmethod
    def getGeneticRange(self):
        return self.env.geneRange

    @classmethod
    def getPopulationSize(self):
        return self.env.populationSize

    @classmethod
    def getNumMaxGenerations(self):
        return self.env.numMaxGenerations

    @classmethod
    def getAllowedError(self):
        return self.env.allowedError

    @classmethod
    def getMutationProbability(self):
        return self.env.mutationProbability

    @classmethod
    def getNetworkLayers(self):
        return self.env.networkLayers

    @classmethod
    def getPatternsInput(self):
        return self.env.patternsInput

    @classmethod
    def getPatternsOutput(self):
        return self.env.patternsOutput

    @classmethod
    def runNeuralNetwork(self):
        self.inputs.runNeuralNetwork()