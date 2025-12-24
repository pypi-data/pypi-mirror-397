import pandas as pd

from tankoh2 import log
from tankoh2.design.afp.layUpClass import LayUpClass


def importAfpLayUpFromExcel(excelFilePath, runDir, modelName):
    log.infoHeadline("**importAfpLayUpFromExcel")
    SectionDefinition, numberSections = sectionDefinitionImport(excelFilePath)
    LayUpDefinition, LayUpDesign = layupDesignImport(excelFilePath, numberSections)
    CylinderContour, DomeContour = contourImport(excelFilePath)

    afpLayUp = LayUpClass(modelName, numberSections, SectionDefinition, CylinderContour, DomeContour)
    afpLayUp.addLayUp(LayUpDefinition, LayUpDesign)
    afpLayUp.addMaterialDatabase(materialImport(excelFilePath))

    afpLayUp.simulationParameters = simulationParametersImport(excelFilePath)
    afpLayUp.processesDic = ProcessParametersImport(excelFilePath, LayUpDefinition)

    afpLayUp.saveFilesAt = runDir
    afpLayUp.inputFileAt = excelFilePath

    return afpLayUp


def sectionDefinitionImport(exFilePath):
    dataTypes = {"SectionNumber": int, "Dome": bool, "SectionStop": float, "userEdgeSeed": float}
    SectionDefinition = pd.read_excel(
        exFilePath, sheet_name="SectionDefinition", skiprows=1, dtype=dataTypes, usecols="A:D"
    )
    numberSections = SectionDefinition.shape[0]
    return SectionDefinition, numberSections


def layupDesignImport(exFilePath, numberSections):
    dataTypes = {"Layer": int, "Process": str, "Material": str, "Angle": float}
    layupDefinition = pd.read_excel(exFilePath, sheet_name="LayUp", skiprows=1, usecols="A:D", dtype=dataTypes)

    columsToUse = [col for col in range(4, numberSections + 4)]
    layupDesignPD = pd.read_excel(exFilePath, sheet_name="LayUp", skiprows=1, usecols=columsToUse, dtype=int)
    # In case of integer conversion errors reformat all the 0s and 1s in the LayUp Design to Standard
    LayUpDesign = layupDesignPD.to_numpy()
    return layupDefinition, LayUpDesign


def contourImport(exFilePath):
    cyContourPa = pd.read_excel(exFilePath, sheet_name="TankContour", usecols="A:B", skiprows=2, dtype=float)
    cyContourNp = cyContourPa.to_numpy()
    domeContourPa = pd.read_excel(exFilePath, sheet_name="TankContour", usecols="C:D", skiprows=2, dtype=float)
    domeContourNp = domeContourPa.to_numpy()
    return cyContourNp, domeContourNp


def materialImport(exFilePath):
    dataTypes = {
        "Material Name": str,
        "tows": int,
        "bandWidth": float,
        "t": float,
        "phiFiber": float,
        "E1": float,
        "E2": float,
        "Nu12": float,
        "Nu23": float,
        "G12": float,
        "G13": float,
        "G23": float,
        "Efiber": float,
        "G12fiber": float,
        "Nu12fiber": float,
        "Nu23fiber": float,
        "Eres": float,
        "G12res": float,
        "Nu12res": float,
        "Roh": float,
        "Rohfiber": float,
        "Rohres": float,
        "Xt": float,
        "Xc": float,
        "Yt": float,
        "SI": float,
        "St": float,
        "alpha0": float,
        "psi0": float,
        "CTE1": float,
        "CTE2": float,
        "CTE3": float,
    }
    mat = pd.read_excel(exFilePath, sheet_name="Materials", dtype=dataTypes, skiprows=1)
    matDatabase = {}
    for index, row in mat.iterrows():
        matDatabase[mat["Material Name"][index]] = dict(row[1:])
    return matDatabase


def simulationParametersImport(exFilePath):
    # load excel file
    data = pd.read_excel(exFilePath, sheet_name="SimulationParameters")
    # create dictionary from DataFrame while converting to the right dType
    simParameters = {
        row["Parameter"]: convData(row["DataTypeInProgram"], row["Value"]) for index, row in data.iterrows()
    }
    return simParameters


def ProcessParametersImport(exFilePath, LayUpDefinition):
    uniqueProcessNames = LayUpDefinition["Process"].unique()

    sheetsToImportFrom = [process + "ProPara" for process in uniqueProcessNames]
    processesDic = {}
    for i, sheet in enumerate(sheetsToImportFrom):
        # load excel file
        data = pd.read_excel(exFilePath, sheet_name=sheet)
        # create dictionary from DataFrame while converting to the right dType
        parameters = {
            row["Parameter"]: convData(row["DataTypeInProgram"], row["Value"]) for index, row in data.iterrows()
        }
        processesDic[uniqueProcessNames[i]] = parameters
    return processesDic


def convData(dataType, value):
    if dataType == "string":
        value = str(value)
    elif dataType == "boolean":
        if value == "True":
            value = True
        elif value == "False":
            value = False
        else:
            raise Exception("Value {} in SimulationParameters is whether False nor True.".format(value))
    elif dataType == "float":
        value = float(value)
    elif dataType == "integer":
        value = int(value)
    elif dataType == "IntList":
        value = value.split(",")
        value = [int(number) for number in value]
    # elif dataType == "Your New Keyword in the Excel Sheet SimulationParameters":
    #    value = your value conversion
    else:
        raise Exception("In importFromExcel.py dataType could not be matched.")
    return value


def checkSimulationParametersForWrongWriting(simulationParameters):
    # for example false is written as flase
    pass  # Todo implement
