from argparse import ArgumentParser

from tankoh2.design.afp.homLayUp import homLayUp
from tankoh2.design.afp.importFromExcel import importAfpLayUpFromExcel
from tankoh2.design.afp.postProcessing import mainPostProcessing
from tankoh2.design.afp.saveVarForAbqPy import saveForAbaqusPyPre
from tankoh2.design.afp.workflowModules import mainProgramStart, runAbq


def mainAFP(excelFileName, nameRun, abqVersion="abq2024hf4"):
    # Developed for abq2024hf4
    runDir, excelInputFilePathInTmpFolder = mainProgramStart(excelFileName, nameRun)
    layUp = importAfpLayUpFromExcel(excelInputFilePathInTmpFolder, runDir, nameRun)
    layUp.plotContourWithSections()
    layUpHomogenized = homLayUp(layUp)
    saveForAbaqusPyPre(layUpHomogenized, runDir)
    runAbq(abqVersion, runDir, nameRun, useGui=False)
    resultsObjIns = mainPostProcessing(
        abqVersion,
        runDir,
        layUpHomogenized,
        nameRun,
        180,
        1,
        8,
    )

    return resultsObjIns


if __name__ == "__main__":
    argParser = ArgumentParser()
    argParser.add_argument(
        "--abaqusExe",
        help="executable for abaqus (absolute or relative path or executable name)",
        default="abaqus",
    )
    parsedOptions = argParser.parse_args()

    mainAFP("DemoStackingDefinition.xlsx", "Demo", parsedOptions.abaqusExe)
