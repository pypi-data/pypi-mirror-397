import neuralRaven

def main():
    fileName = '../data-test/configurationData'
    fileName2 = '../data-test/trainingData'
    inp = neuralRaven.IO()
    print(inp.fromFiles(fileName, fileName2))


if __name__ == "__main__":
    main()