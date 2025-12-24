import copy
import os

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


def postProcessingInPython(runDir, LayUpClass, nameRun, angleRes, contourRes, minSectionRes):
    allNodesDf = readAllNodesFromInp(os.path.join(runDir, nameRun + ".inp"))
    elementsDic = readAllElementsFromInp(os.path.join(runDir, nameRun + ".inp"))
    searchTree = createcKDTree(allNodesDf)

    contourXR = createXRRangeFromContour(LayUpClass, contourRes, minSectionRes)

    angleContourNodesDic = {}
    nodesWithoutResultsDic = {}
    elements2NodeDic = {}
    layer2LayerDic = {}
    angleRange = np.arange(0.0, 360, angleRes)

    for angle in angleRange:
        xyzRot = rotateXRRange(contourXR[:, 0], contourXR[:, 1], angle)
        angleNodesList = findNodesForXYZRange(xyzRot, searchTree)
        angleContourNodesDic[angle] = list(angleNodesList)  # convert to non-numpy objects, to avoid pickel errors
        nodesWithoutResultsDic, elements2NodeDic, layer2LayerDic = attachAngleNodesToDic(
            LayUpClass,
            angleNodesList,
            nodesWithoutResultsDic,
            elements2NodeDic,
            layer2LayerDic,
            allNodesDf,
            elementsDic,
        )

    return nodesWithoutResultsDic, elements2NodeDic, layer2LayerDic, angleContourNodesDic, allNodesDf


def readAllNodesFromInp(abqInputFilePath):
    nodes = []

    with open(abqInputFilePath, "r") as file:
        lines = file.readlines()
        in_nodes_section = False

        for line in lines:
            if "*Node" in line:
                in_nodes_section = True
                continue

            if in_nodes_section:
                if line.startswith("*"):
                    break  # End of nodes section

                parts = line.strip().split(",")
                node_id = int(parts[0].strip())
                x = float(parts[1].strip())
                y = float(parts[2].strip())
                z = float(parts[3].strip())
                nodes.append([node_id, x, y, z])

    nodesDf = pd.DataFrame(nodes, columns=["node", "x", "y", "z"])
    return nodesDf


def readAllElementsFromInp(abqInputFilePath):
    elements = {}

    with open(abqInputFilePath, "r") as file:
        lines = file.readlines()
        in_elements_section = False

        for line in lines:
            if "*Element" in line:
                in_elements_section = True
                continue

            if in_elements_section:
                if line.startswith("*") and not "*Element" in line:
                    break  # End of nodes section

                parts = line.strip().split(",")
                element_id = int(parts[0].strip())
                nodeList = [int(part.strip()) for part in parts[1:]]
                elements[element_id] = nodeList

    return elements


def createXRRangeFromContour(LayUpObj, contourRes, minPointsPerSection):
    # get contourDef and contourLength List from LayUpObj
    sectionDefinition = LayUpObj.secDef
    contourLength = LayUpObj.contourLengthTank

    iterationLength = 0
    xCyl = []
    xDome = []

    # Cylinder relevant code:
    if LayUpObj.flagCylinderandDomeContour:
        lastDomeSectionNumber = getLastDomeSection(sectionDefinition)

        # Cylinder Loop
        cylinderSections = sectionDefinition[sectionDefinition["Dome"] == False]
        for index, section in cylinderSections.iterrows():
            if section["SectionNumber"] == lastDomeSectionNumber:
                sectionLength = contourLength[0]
            else:
                xEndOfSection = LayUpObj.secBordersAxial[index + 1]

                LayUpObj.createAxialCoordinates2ContourLengthFunction()
                sectionLength = LayUpObj.contourLengthAsFunOfAxialPosition(xEndOfSection)
            secRange = np.arange(iterationLength, sectionLength, contourRes)
            if secRange.size < minPointsPerSection:
                secRange = np.arange(
                    iterationLength, sectionLength, (sectionLength - iterationLength) / minPointsPerSection
                )
            iterationLength = sectionLength

            xSection = LayUpObj.axialCylLengthAsAFunOfContourLength(secRange)

            [xCyl.append(xi) for xi in xSection]
        xCyl = np.array(xCyl)
        xCyl = xCyl.reshape(-1, 1)
        rCyl = LayUpObj.cylInterFun(xCyl)

    # Dome relevant code:
    domeSections = sectionDefinition[sectionDefinition["Dome"] == True]
    domeContourLength = contourLength[1] - contourLength[0]
    iterationLength = contourLength[0]
    for index, section in domeSections.iterrows():
        sectionLength = section["SectionStop"] * domeContourLength + contourLength[0]
        secRange = np.arange(iterationLength, sectionLength, contourRes)
        if secRange.size < minPointsPerSection:
            secRange = np.arange(
                iterationLength, sectionLength, (sectionLength - iterationLength) / minPointsPerSection
            )
        iterationLength = sectionLength

        xSection = LayUpObj.axialDomeLengthAsAFunOfContourLength(secRange)

        [xDome.append(xi) for xi in xSection]
    # append last contour point
    xDome.append(LayUpObj.domeContourXYInput[-1, 0])
    # convert 2 numpy and use interpolation function
    xDome = np.array(xDome)
    xDome = xDome.reshape(-1, 1)
    rDome = LayUpObj.domeInterFun(xDome)

    # combine x- and r-array
    domeXR = np.concatenate((xDome, rDome), axis=1)
    if LayUpObj.flagCylinderandDomeContour:
        # Combine
        cylXR = np.concatenate((xCyl, rCyl), axis=1)
        contourXR = np.concatenate((cylXR, domeXR), axis=0)
    else:
        contourXR = domeXR

    return contourXR


def getLastDomeSection(sectionDefinition):
    cylinderSections = sectionDefinition[sectionDefinition["Dome"] == False]
    lastDomeSection = cylinderSections.iloc[-1]
    lastDomeSectionNumber = lastDomeSection["SectionNumber"]
    return lastDomeSectionNumber


def rotateXRRange(x, r, angle):
    y = r * np.cos(np.deg2rad(angle))
    z = r * np.sin(np.deg2rad(angle))

    x = x.reshape(-1, 1)
    y = y.reshape(-1, 1)
    z = z.reshape(-1, 1)

    return np.concatenate((x, y, z), axis=1)


def createcKDTree(allNodesDf):
    # Extract spatial coordinates for building the k-d tree
    nodes = allNodesDf[["x", "y", "z"]]

    # Build the k-d tree using only the spatial coordinates

    return cKDTree(nodes.values)


def findNodesForXYZRange(xyzRot, searchTree):
    _, nodeArray = searchTree.query(xyzRot, k=1)
    nodeArray = nodeArray + 1  # +1 to change from index to node number
    nodeArray = np.unique(nodeArray)
    return [int(it) for it in nodeArray]  # convert to non-numpy objects, to avoid pickel errors


def attachAngleNodesToDic(
    LayUpClass, angleNodesList, nodesWithoutResultsDic, elements2NodeDic, layer2LayerDic, allNodesDf, elementsDic
):
    xPosNodes = allNodesDf["x"][np.array(angleNodesList) - 1].to_numpy()

    for sectionIndex in range(LayUpClass.sections):
        secNodes = findNodesWithinSection(sectionIndex, LayUpClass, xPosNodes, angleNodesList)
        secElementNodePairList = findElementsNext2NodesInSection(
            sectionIndex, LayUpClass, elementsDic, allNodesDf, secNodes
        )

        layerList = getLayerList(LayUpClass, sectionIndex)
        nodesWithoutResultsDic = fillNodesDictionary(nodesWithoutResultsDic, secNodes, layerList)
        elements2NodeDic = fillelements2NodeDictionary(elements2NodeDic, secElementNodePairList)
        layer2LayerDic = fillLayer2LayerDictionary(layer2LayerDic, sectionIndex, layerList)
    return nodesWithoutResultsDic, elements2NodeDic, layer2LayerDic


def findNodesWithinSection(sectionIndex, LayUpClass, xPosNodes, nodesList):
    filterLow = LayUpClass.secBordersAxial[sectionIndex] <= xPosNodes
    filterHigh = xPosNodes < LayUpClass.secBordersAxial[sectionIndex + 1]
    sectionFilterIndex = filterLow & filterHigh
    returnNodes = np.array(nodesList)[sectionFilterIndex]
    return [int(it) for it in returnNodes]  # convert to non-numpy objects, to avoid pickel errors


def findElementsNext2NodesInSection(sectionIndex, LayUpClass, elementsDic, allNodesDf, secNodes):
    elementNodePairs = []
    for node in secNodes:
        elementsWithNode = [
            elementNumber for elementNumber, elementNodesList in elementsDic.items() if node in elementNodesList
        ]
        for element in elementsWithNode:
            if elementInSection(element, sectionIndex, elementsDic, allNodesDf, LayUpClass):
                elementNodePairs.append([element, node, sectionIndex])
                break

    return elementNodePairs


def elementInSection(element, sectionIndex, elementsDic, allNodesDf, LayUpClass):
    meanX = meanXPostionOfElement(element, elementsDic, allNodesDf)
    return isInSection(meanX, sectionIndex, LayUpClass)


def meanXPostionOfElement(element, elementsDic, allNodesDf):
    nodes = np.array(elementsDic[element])
    xPos = allNodesDf["x"][nodes - 1].to_numpy()
    return np.mean(xPos)


def isInSection(xPos, sectionIndex, LayUpClass):
    return LayUpClass.secBordersAxial[sectionIndex] < xPos < LayUpClass.secBordersAxial[sectionIndex + 1]


def getLayerList(LayUpClass, sectionIndex):
    layUpSection = LayUpClass.layUpDesign[:, sectionIndex]
    return [index + 1 for index, layer in enumerate(layUpSection) if layer == 1]


def fillNodesDictionary(dictionary, secNodes, layerlist):
    layerDic = createLayerDic(layerlist)
    for node in secNodes:
        layerDic = copy.deepcopy(layerDic)
        dictionary[int(node)] = layerDic  # convert to non-numpy objects, to avoid pickel errors
    return dictionary


def fillelements2NodeDictionary(elements2NodeDic, secElementsList):
    for [elementForNode, node, sectionIndex] in secElementsList:
        if elementForNode in elements2NodeDic:
            # Append to the existing "nodes" list
            elements2NodeDic[elementForNode]["nodes"].append(node)
        else:
            # Create a new entry with "section" and "nodes"
            elements2NodeDic[elementForNode] = {"section": sectionIndex + 1, "nodes": [node]}
    return elements2NodeDic


def fillLayer2LayerDictionary(layer2layerDic, sectionIndex, layerList):
    layerDic = {}
    for i, layer in enumerate(layerList):
        layerDic[i + 1] = layer

    layer2layerDic[sectionIndex + 1] = layerDic
    return layer2layerDic


def createLayerDic(layerList):
    layerDic = {}
    for layer in layerList:
        layerDic[layer] = {}
    return layerDic
