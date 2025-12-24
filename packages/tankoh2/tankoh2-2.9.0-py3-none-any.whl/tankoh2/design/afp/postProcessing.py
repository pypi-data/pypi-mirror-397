from tankoh2 import log
from tankoh2.design.afp.postProcessingAbaqus import getNodeValuesFromODBWithAbaqusPython
from tankoh2.design.afp.postProcessingPython import postProcessingInPython
from tankoh2.design.afp.postProcessingResults import ResultsObj, plotAndSaveFilesAndObj


def mainPostProcessing(
    abqVersion, runDir, LayUpClass, nameRun, angleRes, contourRes, minSectionRes, noOptimisationRun=True
):
    log.infoHeadline("**mainPostProcessing")
    (
        nodesWithoutResultsDic,
        elements2NodesDic,
        layer2LayerDic,
        angleContourNodesDic,
        allNodesDF,
    ) = postProcessingInPython(runDir, LayUpClass, nameRun, angleRes, contourRes, minSectionRes)
    nodesDicWithResults = getNodeValuesFromODBWithAbaqusPython(
        runDir,
        nodesWithoutResultsDic,
        elements2NodesDic,
        layer2LayerDic,
        angleContourNodesDic,
        nameRun,
        abqVersion,
    )

    resultsObjIns = ResultsObj(
        LayUpClass,
        nodesDicWithResults,
        angleContourNodesDic,
        allNodesDF,
        elements2NodesDic,
    )
    if noOptimisationRun:
        plotAndSaveFilesAndObj(resultsObjIns, runDir)
    return resultsObjIns
