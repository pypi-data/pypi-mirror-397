import copy
import sys
from argparse import ArgumentParser
from os.path import join

from abaqusConstants import *
from odbAccess import *
from odbMaterial import *
from odbSection import *
from textRepr import *
from utilities import importForAbqPost, saveAsPickleFile

"""Functions---------------------------------------------------------------------------------------------------------"""

""" Program Start Functions-----------------------------------------------------------------------------------------"""


def createNodeAndElementSets(nodesDicWithoutResults, element2NodeDic, angleContourNodesDic, odb):
    tryCreateNodeSet(nodesDicWithoutResults.keys(), "AllNodesSet", "AFP360TANK-1", odb)
    tryCreateElementSet(element2NodeDic.keys(), "AllElementsSet", "AFP360TANK-1", odb)
    createAngleNodeSets(angleContourNodesDic, "AFP360TANK-1", odb)
    allNodesSet = getNodeSet("AllNodesSet", "AFP360TANK-1", odb)
    allElementsSet = getElementSet("AllElementsSet", "AFP360TANK-1", odb)
    return allNodesSet, allElementsSet


def tryCreateNodeSet(nodeList, setName, instance, odb):
    try:
        createNodeSet(nodeList, setName, instance, odb)
    except:
        print("Node Set: " + setName + " already exists")
    else:
        print("Node Set: " + setName + " created")


def tryCreateElementSet(elementList, setName, instance, odb):
    try:
        createElementSet(elementList, setName, instance, odb)
    except:
        print("Element Set: " + setName + " already exists")
    else:
        print("Element Set: " + setName + " created")


def createNodeSet(nodeList, setName, instance, odb):
    odb.rootAssembly.instances[instance].NodeSetFromNodeLabels(name=setName, nodeLabels=tuple(nodeList))


def createElementSet(elementList, setName, instance, odb):
    odb.rootAssembly.instances[instance].ElementSetFromElementLabels(name=setName, elementLabels=tuple(elementList))


def createAngleNodeSets(angleContourNodesDic, instance, odb):
    for angle in angleContourNodesDic.keys():
        # print(list(angleContourNodesDic[angle]))
        tryCreateNodeSet(list(angleContourNodesDic[angle]), "AngleNodeSet_" + str(angle), instance, odb)


def getNodeSet(setName, instance, odb):
    return odb.rootAssembly.instances[instance].nodeSets[setName]


def getElementSet(setName, instance, odb):
    return odb.rootAssembly.instances[instance].elementSets[setName]


""" Add Element Values Functions-------------------------------------------------------------------------------------"""


def addElementValuesToDic(nodesDicWithoutResults, element2NodeDic, layer2LayerDic, elementSetRegion, odb):
    fieldOutput = odb.steps["StaticGeneralStep"].frames[-1]

    addXValuesLoop(
        "S", sDataGrabFun, nodesDicWithoutResults, element2NodeDic, layer2LayerDic, fieldOutput, elementSetRegion
    )
    addXValuesLoop(
        "LE", leDataGrabFun, nodesDicWithoutResults, element2NodeDic, layer2LayerDic, fieldOutput, elementSetRegion
    )
    addXValuesLoop(
        "LARCFKCRT",
        larcFKCRTDataGrapFun,
        nodesDicWithoutResults,
        element2NodeDic,
        layer2LayerDic,
        fieldOutput,
        elementSetRegion,
    )
    addXValuesLoop(
        "LARCFSCRT",
        larcFSCRTDataGrapFun,
        nodesDicWithoutResults,
        element2NodeDic,
        layer2LayerDic,
        fieldOutput,
        elementSetRegion,
    )
    addXValuesLoop(
        "LARCFTCRT",
        larcFTCRTDataGrapFun,
        nodesDicWithoutResults,
        element2NodeDic,
        layer2LayerDic,
        fieldOutput,
        elementSetRegion,
    )
    addXValuesLoop(
        "LARCMCCRT",
        larcMCCRTDataGrapFun,
        nodesDicWithoutResults,
        element2NodeDic,
        layer2LayerDic,
        fieldOutput,
        elementSetRegion,
    )


def addXValuesLoop(
    xKey, xDataGrabFun, nodesDicWithoutResults, element2NodeDic, layer2LayerDic, fieldOutput, elementSetRegion
):
    element2NodeDic = copy.copy(element2NodeDic)
    xField = fieldOutput.fieldOutputs[xKey]
    subSet = xField.getSubset(region=elementSetRegion, position=INTEGRATION_POINT)
    # prettyPrint(subSet, 3)
    subSetValues = subSet.values
    for i, f in enumerate(subSetValues):
        # print("Index = ", i)
        sectionNumber, layerAbq = getSecNumberAndLayerFromSectionPointString(f.sectionPoint)
        if isMiddleSectionPoint(sectionNumber):
            # print("Section Number = ", sectionNumber)
            nodeNumberList = element2NodeDic[f.elementLabel]["nodes"]
            for node in nodeNumberList:
                layerNumberDic, valueIsMissing = accessIfLayerValueIsMissing(
                    xKey, node, f.elementLabel, layerAbq, nodesDicWithoutResults, element2NodeDic, layer2LayerDic
                )
                if valueIsMissing:
                    xDataGrabFun(nodesDicWithoutResults, node, layerNumberDic, f)


def sDataGrabFun(nodesDicWithoutResults, node, layerNumberDic, f):
    nodesDicWithoutResults[node][layerNumberDic]["S"] = {
        "S11": float(f.data[0]),  # convert to non-numpy objects, to avoid pickel errors
        "S22": float(f.data[1]),
        "S12": float(f.data[3]),
    }


def leDataGrabFun(nodesDicWithoutResults, node, layerNumberDic, f):
    # Logarithmic Strain
    nodesDicWithoutResults[node][layerNumberDic]["LE"] = {
        "LE11": float(f.data[0]),  # convert to non-numpy objects, to avoid pickel errors
        "LE22": float(f.data[1]),
    }


def larcFKCRTDataGrapFun(nodesDicWithoutResults, node, layerNumberDic, f):
    # Larc05 fiber kinking
    nodesDicWithoutResults[node][layerNumberDic]["LarcFkCrt"] = f.data


def larcFSCRTDataGrapFun(nodesDicWithoutResults, node, layerNumberDic, f):
    # Larc05 fiber spitting
    nodesDicWithoutResults[node][layerNumberDic]["LarcFsCrt"] = f.data


def larcFTCRTDataGrapFun(nodesDicWithoutResults, node, layerNumberDic, f):
    # Larc05 fiber tension
    nodesDicWithoutResults[node][layerNumberDic]["LarcFtCrt"] = f.data


def larcMCCRTDataGrapFun(nodesDicWithoutResults, node, layerNumberDic, f):
    # Larc05 matrix cracking
    nodesDicWithoutResults[node][layerNumberDic]["LarcMcCrt"] = f.data


def accessIfLayerValueIsMissing(
    key, node, elementNumber, layerAbq, nodesDicWithoutResults, element2NodeDic, layer2LayerDic
):
    section = element2NodeDic[elementNumber]["section"]
    layerNumber = layer2LayerDic[section][layerAbq]

    if key in nodesDicWithoutResults[node][layerNumber]:
        valueIsMissing = False
    else:
        valueIsMissing = True
    return layerNumber, valueIsMissing


def getSecNumberAndLayerFromSectionPointString(sectionPointString):
    noBrackets = str(sectionPointString)[1:-1]
    pairs = noBrackets.strip("{}").split(",")
    for pair in pairs:
        key1_value1 = pair.strip().split(":")
        key2_value2 = pair.strip().split("=")
        if len(key1_value1) == 2:
            if key1_value1[0] == "'number'":
                sectionNumber = int(key1_value1[1])
        if len(key2_value2) == 2:
            if key2_value2[0].strip() == "Layer":
                layer = int(key2_value2[1].strip()[:-1])
    return sectionNumber, layer


def isMiddleSectionPoint(SectionPointNumber):
    if SectionPointNumber == 2:
        return True
    else:
        number = SectionPointNumber - 2
        return number % 3 == 0


""" Add Node Values Functions----------------------------------------------------------------------------------------"""


def addNodeValuesToDic(nodesDicWithoutResults, nodeSetRegion, odb):
    fieldOutput = odb.steps["StaticGeneralStep"].frames[-1]
    addUValuesToDic(nodesDicWithoutResults, fieldOutput, nodeSetRegion)


def addUValuesToDic(nodesDicWithoutResults, fieldOutput, nodeSetRegion):
    uField = fieldOutput.fieldOutputs["U"]
    uSet = uField.getSubset(region=nodeSetRegion)
    ufieldValues = uSet.values
    # prettyPrint(fieldValues, 2)
    for f in ufieldValues:
        nodesDicWithoutResults[f.nodeLabel]["U"] = {
            "magnitude": f.magnitude,
            "U1": float(f.data[0]),  # convert to non-numpy objects, to avoid pickel errors
            "U2": float(f.data[1]),
            "U3": float(f.data[2]),
        }


def abq_mainPost(runDir):
    nameRun, nodesDicWithoutResults, elements2NodesDic, layer2LayerDic, angleContourNodesDic = importForAbqPost(runDir)
    odbFilename = join(runDir, nameRun + ".odb")
    odb = openOdb(path=odbFilename)

    """Create Sets-------------------------------------------------------------------------------------------------------"""
    allNodesSet, allElementsSet = createNodeAndElementSets(
        nodesDicWithoutResults, elements2NodesDic, angleContourNodesDic, odb
    )
    """Add Element Values------------------------------------------------------------------------------------------------"""
    print("Getting element values in Abaqus")
    addElementValuesToDic(nodesDicWithoutResults, elements2NodesDic, layer2LayerDic, allElementsSet, odb)

    """Add Node Values---------------------------------------------------------------------------------------------------"""
    print("Getting node values in Abaqus")
    addNodeValuesToDic(nodesDicWithoutResults, allNodesSet, odb)

    """Save dictionary as pickle and close odb---------------------------------------------------------------------------"""
    nodesDicWithResults = nodesDicWithoutResults
    saveAsPickleFile(runDir, nodesDicWithResults, "nodesDicWithResults")

    odb.close()


def main():

    argParser = ArgumentParser()
    argParser.add_argument(
        "--runDir",
        help="directory containing odb file",
        default="",
    )
    argParser.add_argument(
        "--scriptFolderPath",
        help="directory containing python scripts",
        default="",
    )
    parsedOptions = argParser.parse_args()

    runDir = parsedOptions.runDir
    if not runDir:
        raise Exception("You must specify a data directory via commandline using --runDir")

    sys.path.append(parsedOptions.scriptFolderPath)
    abq_mainPost(runDir)


if __name__ == "__main__":
    main()
