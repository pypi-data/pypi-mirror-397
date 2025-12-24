import os
import shutil
import subprocess

from patme.femtools.fecall import AbaqusCaller, AbaqusPythonCaeCaller, AbaqusPythonCaller
from patme.service.systemutils import getRunDir

from tankoh2 import log, programDir


def mainProgramStart(excelInputFileName, nameRun):
    log.infoHeadline("***mainAFP program status:")
    runDir = getRunDir(baseName="afp", basePath=os.path.join(programDir, "tmp"), runDirExtension=f"_{nameRun}")
    print(f"**mainProgramStart in folder: {runDir}")
    if not os.path.exists(excelInputFileName):
        excelInputFileNameRelative = os.path.join(os.path.dirname(__file__), "InputFiles", excelInputFileName)
        if not os.path.exists(excelInputFileNameRelative):
            raise FileNotFoundError(f"Could not find excel input file at {excelInputFileName}")
        excelInputFileName = excelInputFileNameRelative
    shutil.copy2(excelInputFileName, runDir)
    newExcelInputFilePath = os.path.join(runDir, os.path.basename(excelInputFileName))
    return runDir, newExcelInputFilePath


def runAbq(abaqusVersion, runDir, nameRun, modelType="360", useGui=True, pythonArgs=None):
    # default Abaqus: abaqus; learningVersion 2024: "abq2024le"
    if pythonArgs is None:
        pythonArgs = []
    log.infoHeadline("**runAbq")

    validModelTypes = ["360"]
    abqPyModulesDir = getAbqScriptFolderPath()
    pythonArgs.append(abqPyModulesDir)
    pythonArgs.append(runDir)
    if modelType == "360":
        pythonScriptFile = os.path.join(abqPyModulesDir, "main360.py")
    else:
        raise Exception(f'Invalid value for modelType "{modelType}". Valid model types are: {validModelTypes}')

    if useGui:
        print("Please close the Abaqus CAE window after the job is done to resume the loop!")
        subprocess.call([abaqusVersion, "cae", f"script={pythonScriptFile}", "--"] + pythonArgs, shell=True, cwd=runDir)
    else:
        kwargs = {
            "abaqusPath": abaqusVersion,
            "runDir": runDir,
            "pythonSkriptPath": pythonScriptFile,
            "arguments": pythonArgs,
        }

        abqCaeCall = AbaqusPythonCaeCaller(**kwargs)
        abqCaeCall.localSubProcessSettings["shell"] = True
        abqCaeCall.run()

        kwargs["feFilename"] = os.path.join(runDir, f"{nameRun}.inp")
        abqCall = AbaqusCaller(**kwargs)
        abqCall.localSubProcessSettings["shell"] = True
        abqCall.run()


def runAbaqusPythonSkript(pythonScriptName, runDir, abaqusVersion="abq2024hf4"):
    """Runs Abaqus Cae script

    :param pythonScriptName: module name to be started
    :param abaqusVersion: version of Abaqus Cae to use
    """
    scriptFolderPath = getAbqScriptFolderPath()
    pythonArgs = ["--scriptFolderPath", scriptFolderPath, "--runDir", runDir]
    kwargs = {
        "abaqusPath": abaqusVersion,
        "runDir": runDir,
        "pythonSkriptPath": os.path.join(scriptFolderPath, pythonScriptName),
        "arguments": pythonArgs,
    }

    abqPyCall = AbaqusPythonCaller(**kwargs)
    abqPyCall.localSubProcessSettings["shell"] = True
    abqPyCall.run()
    return


def getAbqScriptFolderPath():
    return os.path.join(os.path.dirname(__file__), "abqPyModules")


if __name__ == "__main__":
    if 0:
        currentDirectory = os.getcwd()

        fromPath = "InputFiles/DemoStackingDefinition.xlsx"
        toPath = "tmp"

        fromPath = os.path.join(currentDirectory, fromPath)
        toPath = os.path.join(currentDirectory, toPath)

        shutil.copy2(fromPath, toPath)

    if 0:
        programDirectory, newTmpFolderPath, newExcelInputFilePath = mainProgramStart("DemoStackingDefinition.xlsx")
        print(programDirectory)
        print(newTmpFolderPath)
        print(newExcelInputFilePath)

    if 0:
        # runAbq("abq2024le", "360", False) # Learning Version
        runDirTmp = ""
        runAbq("abq2024hf4", runDirTmp, modelType="360", useGui=True)
