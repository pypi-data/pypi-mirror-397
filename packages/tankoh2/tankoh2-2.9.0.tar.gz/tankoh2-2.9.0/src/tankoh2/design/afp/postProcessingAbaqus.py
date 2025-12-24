from tankoh2.design.afp.abqPyModules.utilities import loadFromPickleFile, saveAsPickleFile
from tankoh2.design.afp.workflowModules import runAbaqusPythonSkript


def getNodeValuesFromODBWithAbaqusPython(
    runDir,
    nodesWithoutResultsDic,
    elements2NodesDic,
    layer2LayerDic,
    angleContourNodesDic,
    nameRun,
    abqVersion,
):

    caePostInputDict = {
        "nameRun": nameRun,
        "nodesWithoutResultsDic": nodesWithoutResultsDic,
        "elements2NodesDic": elements2NodesDic,
        "layer2LayerDic": layer2LayerDic,
        "angleContourNodesDic": angleContourNodesDic,
    }
    # write input for CAE Post
    saveAsPickleFile(runDir, caePostInputDict, "caePostInputDict")

    # call CAE
    runAbaqusPythonSkript("abq_ODBDataExtraction.py", runDir, abqVersion)

    # read CAE results
    nodesDicWithResults = loadFromPickleFile(runDir, "nodesDicWithResults")
    return nodesDicWithResults
