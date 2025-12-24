"""
module for functions commonly used in regular tankoh2 and abq_python
"""

import json
import os
import pickle
from os.path import join

import numpy as np


def saveAsPickleFile(path, data, filename):
    with open(join(path, filename + ".pkl"), "wb") as fp:
        pickle.dump(data, fp)


def loadFromPickleFile(directory, filename):
    with open(os.path.join(directory, filename + ".pkl"), "rb") as fp:
        data = pickle.load(fp)
    return data


def importForAbqPost(basePath):

    data = loadFromPickleFile(basePath, "caePostInputDict")

    nameRun = data["nameRun"]
    nodesWithoutResultsDic = data["nodesWithoutResultsDic"]
    elements2NodesDic = data["elements2NodesDic"]
    layer2LayerDic = data["layer2LayerDic"]
    angleContourNodesDic = data["angleContourNodesDic"]
    return nameRun, nodesWithoutResultsDic, elements2NodesDic, layer2LayerDic, angleContourNodesDic


def importForAbqPre(runDir):
    # load numpy arrays
    loadedNumpyKwArgs = np.load(join(runDir, "caePreInput.npz"))
    cyCoordinates = loadedNumpyKwArgs["cyCoordinates"]
    domeCoordinates = loadedNumpyKwArgs["domeCoordinates"]
    secBordersAxial = loadedNumpyKwArgs["secBordersAxial"]
    secBordersRadius = loadedNumpyKwArgs["secBordersRadius"]
    edgeSeedUserInput = loadedNumpyKwArgs["edgeSeedUserInput"]
    layUpDesign = loadedNumpyKwArgs["layUpDesign"]
    projectedSecAngle = loadedNumpyKwArgs["projectedSecAngle"]
    radiusChangeInCyl = loadedNumpyKwArgs["radiusChangeInCyl"]
    sectionBorderPoints = []
    for i, sec in enumerate(secBordersAxial):
        sectionBorderPoints.append((sec, secBordersRadius[i], 0))

    # load json data
    with open(join(runDir, "caePreInput.json"), "r") as f:
        loadedJsonKwArgs = json.load(f)
    homMatDatabase = loadedJsonKwArgs["homMatDatabase"]
    matDatabase = loadedJsonKwArgs["matDatabase"]
    processList = loadedJsonKwArgs["processList"]
    simulationParametersDic = loadedJsonKwArgs["simulationParametersDic"]
    modelName = loadedJsonKwArgs["modelName"]

    return (
        modelName,
        cyCoordinates,
        domeCoordinates,
        matDatabase,
        homMatDatabase,
        sectionBorderPoints,
        edgeSeedUserInput,
        layUpDesign,
        projectedSecAngle,
        processList,
        radiusChangeInCyl,
        simulationParametersDic,
    )
