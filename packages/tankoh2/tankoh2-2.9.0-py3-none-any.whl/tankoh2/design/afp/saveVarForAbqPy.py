import json
from os.path import join

import numpy as np

from tankoh2 import log
from tankoh2.service.utilities import NpEncoderWarn


def saveForAbaqusPyPre(layUp, runDir):
    log.infoHeadline("**saveForAbaqusPy")
    data = getAndConvertVariablesForAbqPy(layUp)
    writeAbqPyInputPre(runDir, *data)


def getAndConvertVariablesForAbqPy(afpTankInstance):
    # Model Name:
    modelName = afpTankInstance.name
    # Cylinder Contour:
    cyCoordinates = afpTankInstance.cylinderContourXYInput
    # Dome Contour:
    domeCoordinates = afpTankInstance.domeContourXYInput
    # Materials Database:
    matDatabase = afpTankInstance.materialDatabase
    # Homogenized Materials Dictionary:
    homMatDatabase = afpTankInstance.homMatProp
    # extract points that define the section borders
    secBordersAxial = afpTankInstance.secBordersAxial
    secBordersRadius = afpTankInstance.secBordersRadius
    edgeSeedUserInput = afpTankInstance.secDef["UserEdgeSeed"].to_numpy()
    # extract LayUp Design
    layUpDesign = afpTankInstance.layUpDesign
    # extract projected Angles
    projectedSecAngle = afpTankInstance.projectedSecAngle
    # extract Process List
    processList = afpTankInstance.layUpDefinition["Process"].to_list()
    # extract Radius Change in Cylinder Array
    radiusChangeInCyl = afpTankInstance.SlopeChangeCyl
    # extract SimulationParameters
    simulationParametersDic = afpTankInstance.simulationParameters

    return (
        modelName,
        cyCoordinates,
        domeCoordinates,
        matDatabase,
        homMatDatabase,
        secBordersAxial,
        secBordersRadius,
        edgeSeedUserInput,
        layUpDesign,
        projectedSecAngle,
        processList,
        radiusChangeInCyl,
        simulationParametersDic,
    )


def writeAbqPyInputPre(
    runDir,
    modelName,
    cyCoordinates,
    domeCoordinates,
    matDatabase,
    homMatDatabase,
    secBordersAxial,
    secBordersRadius,
    edgeSeedUserInput,
    layUpDesign,
    projectedSecAngle,
    processList,
    radiusChangeInCyl,
    simulationParametersDic,
):

    # save pre processing data
    numpyKwArgs = {
        "cyCoordinates": cyCoordinates,
        "domeCoordinates": domeCoordinates,
        "secBordersAxial": secBordersAxial,
        "secBordersRadius": secBordersRadius,
        "edgeSeedUserInput": edgeSeedUserInput,
        "layUpDesign": layUpDesign,
        "projectedSecAngle": projectedSecAngle,
        "radiusChangeInCyl": radiusChangeInCyl,
    }
    np.savez(join(runDir, "caePreInput"), allow_pickle=False, **numpyKwArgs)

    jsonKwArgs = {
        "homMatDatabase": homMatDatabase,
        "matDatabase": matDatabase,
        "processList": processList,
        "simulationParametersDic": simulationParametersDic,
        "modelName": modelName,
    }
    with open(join(runDir, "caePreInput.json"), "w") as f:
        json.dump(jsonKwArgs, f, indent=2, cls=NpEncoderWarn)
