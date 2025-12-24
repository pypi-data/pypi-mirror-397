import sys

import interaction
import step
from abaqus import *
from abaqusConstants import *

abqPyModulesDir, runDir = sys.argv[-2:]
sys.path.append(abqPyModulesDir)

from abq_functions import (
    assignLayUptoSections,
    createAllMaterials,
    createAssembly,
    createAxialAndPolarDatum,
    createBC360tank,
    createCompositesFieldOutput,
    createConstraintCoupling,
    createDatumPlanesXZandXYplane,
    createHomogenTemperatureFields,
    createJob,
    createLoad,
    createPartions,
    createSets360Tank,
    createStep,
    createTankGeoOpenPolar,
    insertLarcToFieldOutput,
    meshWithEdgeSeed360FreeControl,
)
from utilities import importForAbqPre

session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

"Import from transfer folder-------------------------------------------------------------------------------------------"
(
    modelName,
    cyCoordinates,
    domeCoordinates,
    matProp,
    homMatProp,
    partitionBorderPoints,
    edgeSeedUserInput,
    layUpDesign,
    projectedSecAngle,
    processList,
    radiusChangeInCyl,
    simulationParametersDic,
) = importForAbqPre(runDir)
"Create model----------------------------------------------------------------------------------------------------------"
my_model = mdb.Model(name=modelName)
"Create geometry-------------------------------------------------------------------------------------------------------"
afpPart = createTankGeoOpenPolar(my_model, cyCoordinates, domeCoordinates, radiusChangeInCyl)
"Create Datums---------------------------------------------------------------------------------------------------------"
createAxialAndPolarDatum(afpPart, domeCoordinates[-2, 0])
createDatumPlanesXZandXYplane(afpPart)
"Create Sets-----------------------------------------------------------------------------------------------------------"
createSets360Tank(afpPart, partitionBorderPoints)
"Create all materials--------------------------------------------------------------------------------------------------"
createAllMaterials(my_model, matProp, homMatProp, simulationParametersDic["refTemperatureMaterial"])
"Create partions-------------------------------------------------------------------------------------------------------"
pointsOnSections = createPartions(afpPart, partitionBorderPoints, 10, radiusChangeInCyl)
"Assign LayUp to Section"
assignLayUptoSections(
    afpPart,
    pointsOnSections,
    layUpDesign,
    projectedSecAngle,
    matProp,
    homMatProp,
    processList,
    4,
    3,
)
"Create Assembly-------------------------------------------------------------------------------------------------------"
my_instance, my_csys = createAssembly(my_model, afpPart)
"Create Step-----------------------------------------------------------------------------------------------------------"
createStep(my_model)
"Create Field Output Functions-----------------------------------------------------------------------------------------"
createCompositesFieldOutput(my_model, layUpDesign)
"Create Coupling-------------------------------------------------------------------------------------------------------"
createConstraintCoupling(my_model, partitionBorderPoints[0], 5, 4)
"Create BC-------------------------------------------------------------------------------------------------------------"
createBC360tank(my_model, 5)
"Create Load-----------------------------------------------------------------------------------------------------------"
createLoad(my_model, my_instance, "innerTankInsideSurf", "StaticGeneralStep", simulationParametersDic["pressure"])
"Create Temperature Fields---------------------------------------------------------------------------------------------"
if simulationParametersDic["thermalLoadOn"]:
    createHomogenTemperatureFields(
        my_model, simulationParametersDic["initialStepTemperature"], simulationParametersDic["loadStepTemperature"]
    )
"Create Mesh-----------------------------------------------------------------------------------------------------------"
meshWithEdgeSeed360FreeControl(
    afpPart,
    simulationParametersDic["maxElmSizePartSeed"],
    simulationParametersDic["minElmSizePartSeed"],
    simulationParametersDic["edgeSeedSize"],
    partitionBorderPoints,
    edgeSeedUserInput,
)
# meshWithGradientEdgeSeed360SweepControl(afpPart, 100, 50, partionBorderPoints, deviFactor=0.15)
"Add Larc to FieldOutput in Keyword Block------------------------------------------------------------------------------"
insertLarcToFieldOutput(my_model)
"Write Input File------------------------------------------------------------------------------------------------------"
createJob(my_model, runDir)
