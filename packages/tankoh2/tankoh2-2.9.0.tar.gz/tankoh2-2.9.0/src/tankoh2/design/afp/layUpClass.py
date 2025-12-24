import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

from tankoh2 import log
from tankoh2.design.afp.afpProcessImplementations import (
    CSTable,
    IsoAngleSteeringProcess,
    IsoAngSteerLimitsV1,
    PolarPatchProcess,
    WindingStyleGeoProcess,
)


class LayUpClass:
    def __init__(self, name, sections, sectionDefinitions, cylinderContourXY, domeContourXY):
        # initial value allocation attributes:
        self.name = name
        self.saveFilesAt = "tmp/"
        self.sections = int(sections)
        self.secDef = sectionDefinitions  # pd.DataFrame[{"SectionNumber": int,"Dome": Boolean,"SectionStop": float}]
        self.flagCylinderandDomeContour = self.checkForCylinderSections(sectionDefinitions)  # boolean
        self.cylinderContourXYInput = self.cleanCylinderContourXYInputFromNaNValues(cylinderContourXY)  # numpy 2D array
        self.domeContourXYInput = domeContourXY  # numpy 2D array
        self.axialLengthTank = self.calculateAxialLength()
        self.contourLengthTank = self.calculateContourLength()
        self.interpolatedTankContourXY = self.contourInterpolation()
        self.secBordersAxial = self.splitAxialSecCoordinates()  # numpy 1D array
        self.secBordersRadius = self.calcRadiusOfBorderPoints()
        self.SlopeChangeCyl = self.calcSlopeChangesInCylinder()
        # non-initial value allocation attributes:
        self.inputFileAt = ""
        self.materialDatabase = {}
        self.processesDic = {}
        self.simulationParameters = {}
        self.homMatProp = {}
        self.layUpDefinition = pd.DataFrame([])
        self.layUpDesign = np.array([])
        self.projectedSecAngle = np.array([])

    def checkForCylinderSections(self, sectionDefinitions):
        return any(not domeSectionFlag for domeSectionFlag in sectionDefinitions["Dome"])

    def cleanCylinderContourXYInputFromNaNValues(self, cylinderContourXY):
        return cylinderContourXY[np.isfinite(cylinderContourXY)].reshape((-1, 2))

    def calculateAxialLength(self):
        if self.flagCylinderandDomeContour:
            cylinderAxialLength = self.cylinderContourXYInput[-1, 0] - self.cylinderContourXYInput[0, 0]
        else:
            cylinderAxialLength = 0
        domeAxialLength = self.domeContourXYInput[-1, 0] - self.domeContourXYInput[0, 0]
        return [cylinderAxialLength, cylinderAxialLength + domeAxialLength]

    def calculateContourLength(self):
        if self.flagCylinderandDomeContour:
            self.createCylInterFun()
        self.createDomeInterFun()

        cylinderContourLength = 0

        if self.flagCylinderandDomeContour:
            (
                cylinderContourLength,
                self.axialCylLengthAsAFunOfContourLength,
            ) = self.createAxialLengthAsAFunOfContourLengthFun(
                self.cylInterFun,
                self.cylinderContourXYInput[0, 0],
                self.cylinderContourXYInput[-1, 0],
                0,
            )

        (
            cylinderAndDomeContourLength,
            self.axialDomeLengthAsAFunOfContourLength,
        ) = self.createAxialLengthAsAFunOfContourLengthFun(
            self.domeInterFun,
            self.domeContourXYInput[0, 0],
            self.domeContourXYInput[-1, 0],
            cylinderContourLength,
        )

        return [cylinderContourLength, cylinderAndDomeContourLength]

    def createCylInterFun(self):
        self.cylInterFun = interpolate.interp1d(self.cylinderContourXYInput[:, 0], self.cylinderContourXYInput[:, 1])

    def createDomeInterFun(self):
        self.domeInterFun = interpolate.CubicSpline(self.domeContourXYInput[:, 0], self.domeContourXYInput[:, 1])

    def createAxialLengthAsAFunOfContourLengthFun(
        self,
        interpolationFun,
        axialPositionIntegrationStart,
        axialPositionIntegrationEnd,
        contourLengthAtIntegrationStart,
        nIntSamples=8000,
    ):
        xSamples = np.linspace(axialPositionIntegrationStart, axialPositionIntegrationEnd, nIntSamples)
        ySamples = interpolationFun(xSamples)

        xdiff = np.diff(xSamples)
        ydiff = np.diff(ySamples)

        contourDiff = np.sqrt(xdiff**2 + ydiff**2)
        contourDiff = np.insert(contourDiff, 0, 0)

        contourLength = np.cumsum(contourDiff) + contourLengthAtIntegrationStart

        axialLengthAsAFunOfContourLength = interpolate.interp1d(contourLength, xSamples)

        return contourLength[-1], axialLengthAsAFunOfContourLength

    def contourInterpolation(self, nSamples=8000):
        nSamplesCylinder = 0
        if self.flagCylinderandDomeContour:
            # Cylinder
            nSamplesCylinder = int(nSamples * self.contourLengthTank[0] / self.contourLengthTank[1])
            xCy = np.linspace(self.cylinderContourXYInput[0, 0], self.cylinderContourXYInput[-1, 0], nSamplesCylinder)
            xCy = xCy[:-1]  # since last point of cyl is identical first point of dome , avoid to have point 2 times
            xCy = np.reshape(xCy, (-1, 1))
            yCy = self.cylInterFun(xCy)
            cyXY = np.concatenate((xCy, yCy), axis=1)
        # Dome
        xDome = np.linspace(self.domeContourXYInput[0, 0], self.domeContourXYInput[-1, 0], nSamples - nSamplesCylinder)
        xDome = np.reshape(xDome, (-1, 1))
        yDome = self.domeInterFun(xDome)
        domeXY = np.concatenate((xDome, yDome), axis=1)
        if self.flagCylinderandDomeContour:
            # Combine
            interpolatedContour = np.concatenate((cyXY, domeXY), axis=0)
        else:
            interpolatedContour = domeXY

        return interpolatedContour

    def createAxialCoordinates2ContourLengthFunction(self):
        xDomeContour = np.linspace(self.contourLengthTank[0], self.contourLengthTank[1], 100)
        xDomeAxial = self.axialDomeLengthAsAFunOfContourLength(xDomeContour)

        if self.flagCylinderandDomeContour:
            xCylContour = np.linspace(0, self.contourLengthTank[0], 100)
            xCylAxial = self.axialCylLengthAsAFunOfContourLength(xCylContour)

            xAxial = np.concatenate((xCylAxial[:-1], xDomeAxial), axis=0)
            xContour = np.concatenate((xCylContour[:-1], xDomeContour), axis=0)
        else:
            xAxial = xDomeAxial
            xContour = xDomeContour

        self.contourLengthAsFunOfAxialPosition = interpolate.interp1d(xAxial, xContour)

    def splitAxialSecCoordinates(self):
        sectionDefinitionPoints = [self.interpolatedTankContourXY[0, 0]]
        sectionIndex = self.secDef.shape[0]
        contourLengthDome = self.contourLengthTank[1] - self.contourLengthTank[0]

        lineCountCylXY = 1
        for sectionIndex in range(sectionIndex):
            if self.secDef.iloc[sectionIndex]["Dome"]:
                sectionContourLength = (
                    contourLengthDome * self.secDef.iloc[sectionIndex]["SectionStop"] + self.contourLengthTank[0]
                )
                sectionDefinitionPoints.append(self.axialDomeLengthAsAFunOfContourLength(sectionContourLength))
            else:
                sectionDefinitionPoints, lineCountCylXY = self.appendCylinderSections(
                    sectionIndex, lineCountCylXY, sectionDefinitionPoints
                )
        return np.array(sectionDefinitionPoints)

    def appendCylinderSections(self, sectionIndex, lineCountCylXY, sectionDefinitionPoints):
        if self.secDef.iloc[sectionIndex]["SectionStop"] == 1001:
            sectionDefinitionPoints.append(self.cylinderContourXYInput[lineCountCylXY, 0])
            lineCountCylXY = lineCountCylXY + 1
        else:
            axialSectionStop = self.axialCylLengthAsAFunOfContourLength(
                self.contourLengthTank[0] * self.secDef.iloc[sectionIndex]["SectionStop"]
            )
            if axialSectionStop < sectionDefinitionPoints[-1]:
                raise Exception(
                    f"Axial position of section {sectionIndex + 1} is smaller than section {sectionIndex}, must be "
                    f"greater! Increase axial position of section {sectionIndex + 1} or decrease of section "
                    f"{sectionIndex}.",
                )
            else:
                sectionDefinitionPoints.append(axialSectionStop)
        return sectionDefinitionPoints, lineCountCylXY

    def calcRadiusOfBorderPoints(self):
        if self.flagCylinderandDomeContour:
            cyRadie = np.array([self.cylInterFun(x) for x in self.secBordersAxial if x <= self.axialLengthTank[0]])
        domeRadie = np.array([self.domeInterFun(x) for x in self.secBordersAxial if x > self.axialLengthTank[0]])
        if self.flagCylinderandDomeContour:
            # Combine
            radieOfBorderPoints = np.concatenate((cyRadie, domeRadie), axis=0)
        else:
            radieOfBorderPoints = domeRadie
        return radieOfBorderPoints

    def calcSlopeChangesInCylinder(self):
        if self.flagCylinderandDomeContour:
            nCylSec = self.numberCylSec()
            cylSlopes = self.calculateSlopesInCylinder(nCylSec)

            firstSlope = cylSlopes[0]
            slopeChangeList = []
            for secondSlope in cylSlopes[1:]:
                slopeChangeList.append(secondSlope != firstSlope)
                firstSlope = secondSlope
            return slopeChangeList

        else:
            return []

    def numberCylSec(self):
        filter = True != self.secDef["Dome"].to_numpy()
        return len(self.secDef["Dome"][filter])

    def calculateSlopesInCylinder(self, nCylSec):
        xdiff = np.diff(self.secBordersAxial[: nCylSec + 1])
        ydiff = np.diff(self.secBordersRadius[: nCylSec + 1])
        return np.divide(ydiff, xdiff)

    def addMaterial(self, Name, propertiesDic):
        self.materialDatabase[Name] = propertiesDic

    def addMaterialDatabase(self, materialDatabase):
        self.materialDatabase = materialDatabase

    def addLayUp(self, LayUpDef, LayUpDesign):
        if not LayUpDesign.shape[1] == self.sections or LayUpDef.shape[0] == self.sections:
            raise Exception("Shape of LayUpDef or LayUpDesign does not match the number of sections!!!")
        # dataframe={"Layer": int, "Process": String, "Material": String, "Angle": float}
        # number of columns with "Sec-n" must match self.sections
        self.layUpDefinition = pd.concat([self.layUpDefinition, LayUpDef], ignore_index=True)
        self.uniqueProcessNames = self.layUpDefinition["Process"].unique()
        self.layUpDesign = LayUpDesign
        self.projectedSecAngle = np.empty(self.layUpDesign.shape)
        self.projectedSecAngle[:] = np.nan
        self.projectedSecPhiGap = np.empty(self.layUpDesign.shape)
        self.projectedSecPhiGap[:] = np.nan

    def projectAngles(self, flagTowCuttingStartAtDomeStart=True, flagGapFunctionOn=True):
        if flagGapFunctionOn:
            log.info("Projecting Angles with gap function turned on")
            if flagTowCuttingStartAtDomeStart:
                log.info("and tow cutting starting at the dome start")
            else:
                log.info("and tow cutting starting at the cylinder start")
        else:
            log.info("Projecting Angles with gap function turned off")

        # reset projected angles:
        self.projectedSecAngle[:] = np.nan
        self.projectedSecPhiGap[:] = np.nan
        # process selection:
        for processName in self.uniqueProcessNames:
            if processName == "IsoAngleSteering":
                processVariables = {}
                processIns = IsoAngleSteeringProcess(processName, self.processesDic[processName])
                self.startProcessLoop(
                    processIns, processName, processVariables, True, flagTowCuttingStartAtDomeStart, flagGapFunctionOn
                )
            elif processName == "PolarPatch":
                processVariables = {}
                processIns = PolarPatchProcess(processName, self.processesDic[processName])
                self.startProcessLoop(
                    processIns, processName, processVariables, False, flagTowCuttingStartAtDomeStart, flagGapFunctionOn
                )
            elif processName == "WindingStyleGeo":
                processVariables = {}
                processIns = WindingStyleGeoProcess(processName, self.processesDic[processName])
                self.startProcessLoop(
                    processIns, processName, processVariables, True, flagTowCuttingStartAtDomeStart, flagGapFunctionOn
                )
            elif processName == "IsoAngSteerLimitsV1":
                processVariables = {}
                processIns = IsoAngSteerLimitsV1(processName, self.processesDic[processName])
                self.startProcessLoop(
                    processIns, processName, processVariables, True, flagTowCuttingStartAtDomeStart, flagGapFunctionOn
                )
            elif processName == "CSTable":
                processVariables = {
                    "xOffsetDomeStart": self.domeContourXYInput[0, 0],
                    "xOffsetDomeEnd": self.domeContourXYInput[-1, 0],
                }
                processIns = CSTable(processName, self.processesDic[processName], self.inputFileAt)
                self.startProcessLoop(
                    processIns, processName, processVariables, True, flagTowCuttingStartAtDomeStart, flagGapFunctionOn
                )
            # elif processName == "yourNewUniqueProcessName":
            #     processVariables = {}  # add parameters to the dictionary if required for your process evaluation
            #     processWithGaps = True  # True if your process calculates gapshares
            #     processIns = yourImplementedProcess(processName, self.processesDic[processName])
            #     self.startProcessLoop(
            #         processIns, processName, processVariables, processWithGaps, FlagTowCuttingStartAtDomeStart,
            #         FlagGapFunctionOn
            #     )
            else:
                raise Exception("You created a new process? Please add your new process to the loop in projectAngles.")

    def startProcessLoop(
        self,
        processInstance,
        processName,
        processVariables,
        processWithGaps,
        FlagTowCuttingStartAtDomeStart,
        FlagGapFunctionOn,
    ):
        processLayers = self.layUpDefinition.loc[self.layUpDefinition["Process"] == processName]
        self.processLoop(
            processLayers,
            processInstance,
            processVariables,
            processWithGaps,
            FlagTowCuttingStartAtDomeStart,
            FlagGapFunctionOn,
        )

    def processLoop(
        self,
        processLayers,
        processIns,
        processVariables,
        processWithGaps,
        flagTowCuttingStartAtDomeStart,
        flagGapFunctionOn,
    ):
        for iLayer in processLayers["Layer"]:
            plotDir = ""
            if self.simulationParameters["plotGapAndAngleFunction"]:
                if iLayer in self.simulationParameters["plotGapAndAngleFunctionForLayers"]:
                    plotDir = self.saveFilesAt

            y = self.interpolatedTankContourXY[:, 1]
            x = self.interpolatedTankContourXY[:, 0]
            projectedAngles, angleFunDefined, notExceedingSteeringLimit = processIns.evaluateProcess(
                x,
                y,
                self.layUpDefinition["Angle"][iLayer - 1],
                iLayer,
                plotDir=plotDir,
                evaluationArg=processVariables,
            )

            if processWithGaps:
                phiGapProjectedArray, gapFunctionDefined = self.projectGaps(
                    processIns,
                    x,
                    y,
                    projectedAngles,
                    iLayer,
                    flagTowCuttingStartAtDomeStart,
                    flagGapFunctionOn,
                    plotDir=plotDir,
                    evaluationArg=processVariables,
                )

            sectionIndexWith1 = [j + 1 for j, val in enumerate(self.layUpDesign[iLayer - 1, :]) if val == 1]
            for section in sectionIndexWith1:
                filterIndex = self.giveFilterIndexValuesOfSection(section)
                if any(np.invert(angleFunDefined[filterIndex])):
                    processIns.evaluateProcess(
                        x,
                        y,
                        self.layUpDefinition["Angle"][iLayer - 1],
                        iLayer,
                        plotDir=self.saveFilesAt,
                        evaluationArg=processVariables,
                    )
                    raise Exception(
                        "Angle Function is not defined in Layer {} Section {}. Have a look at the process evaluation "
                        "in tmp folder".format(iLayer, section)
                    )
                if any(np.invert(notExceedingSteeringLimit[filterIndex])):
                    processIns.evaluateProcess(
                        x,
                        y,
                        self.layUpDefinition["Angle"][iLayer - 1],
                        iLayer,
                        plotDir=self.saveFilesAt,
                        evaluationArg=processVariables,
                    )
                    raise Exception(
                        "Steering Limit exceeded in Layer {} Section {}. Have a look at the process evaluation "
                        "in tmp folder".format(iLayer, section)
                    )
                if processWithGaps and flagGapFunctionOn:
                    if any(np.invert(gapFunctionDefined[filterIndex])):
                        self.projectGaps(
                            processIns,
                            x,
                            y,
                            projectedAngles,
                            iLayer,
                            flagTowCuttingStartAtDomeStart,
                            flagGapFunctionOn,
                            plotDir=self.saveFilesAt,
                            evaluationArg=processVariables,
                        )
                        raise Exception(
                            "Gap Function is not defined in Layer {} Section {}. Have a look at the process evaluation "
                            "in tmp folder".format(iLayer, section)
                        )
                self.calculateAngleMeanValueOfSectionAndSaveItInTheProjectedSecAngleMatrix(
                    iLayer, section, projectedAngles[filterIndex]
                )
                if processWithGaps:
                    self.calculatephiGapMaxValueOfSectionAndSaveItInTheProjectedSecAngleMatrix(
                        iLayer, section, phiGapProjectedArray[filterIndex]
                    )

    def calculateAngleMeanValueOfSectionAndSaveItInTheProjectedSecAngleMatrix(self, layer, section, array):
        try:
            self.projectedSecAngle[layer - 1, section - 1] = self.meanWithInputCheck(array)
        except:
            raise Exception(
                "For Layer {0} Section {1} the projected angle values contain NAN values!".format(layer, section)
            )

    def calculatephiGapMaxValueOfSectionAndSaveItInTheProjectedSecAngleMatrix(self, layer, section, array):
        try:
            self.projectedSecPhiGap[layer - 1, section - 1] = self.maxWithInputCheck(array)
        except:
            raise Exception(
                "For Layer {0} Section {1} the projected phiGap values contain NAN values!".format(layer, section)
            )

    def maxWithInputCheck(self, array):
        if np.isnan(array).any():
            raise Exception("Nan value in mean calculation. No element in the array should be of type Nan!")
        return np.max(array)

    def meanWithInputCheck(self, array):
        if np.isnan(array).any():
            raise Exception("Nan value in mean calculation. No element in the array should be of type Nan!")
        return np.mean(array)

    def giveFilterIndexValuesOfSection(self, section):
        filterMax = self.secBordersAxial[section] > self.interpolatedTankContourXY[:, 0]
        filterMin = self.secBordersAxial[section - 1] < self.interpolatedTankContourXY[:, 0]
        sectionFilter = filterMin & filterMax
        if not any(sectionFilter):
            raise Exception(
                "For Section {} no filtering range could be found. The problem can possibly solved by increasing the contour resolution.".format(
                    section
                )
            )
        return sectionFilter

    def projectGaps(
        self,
        processInstance,
        axialArray,
        radiusArray,
        projectedAngles,
        layer,
        FlagTowCuttingStartAtDomeStart=True,
        FlagGapFunctionOn=True,
        plotDir="",
        evaluationArg={},
    ):
        if FlagGapFunctionOn:
            if FlagTowCuttingStartAtDomeStart:
                numberCylSections = self.numberCylSec()
                axialStartDome = self.secBordersAxial[numberCylSections]
                indexDome = axialArray >= axialStartDome
                indexCyl = axialArray < axialStartDome

                axialArrayDome = axialArray[indexDome]
                radiusArrayDome = radiusArray[indexDome]
                projectedAnglesDome = projectedAngles[indexDome]
                phiGapProjectedArrayDome, phiGapFunDefinedDome = processInstance.evaluatePhiGap(
                    axialArrayDome,
                    radiusArrayDome,
                    projectedAnglesDome,
                    self.getLayerMaterial(layer),
                    layer,
                    plotDir=plotDir,
                    evaluationArg=evaluationArg,
                )

                radiusArrayCyl = radiusArray[indexCyl]
                phiGapProjectedCylArray = np.zeros(radiusArrayCyl.shape)
                phiGapFunDefinedCyl = np.full(radiusArrayCyl.shape, True)

                phiGapProjectedArray = np.concatenate([phiGapProjectedCylArray, phiGapProjectedArrayDome])
                phiGapFunDefined = np.concatenate([phiGapFunDefinedCyl, phiGapFunDefinedDome])
            else:
                phiGapProjectedArray, phiGapFunDefined = processInstance.evaluatePhiGap(
                    axialArray,
                    radiusArray,
                    projectedAngles,
                    self.getLayerMaterial(layer),
                    layer,
                    plotDir=plotDir,
                    evaluationArg=evaluationArg,
                )
        else:
            phiGapProjectedArray = np.zeros(radiusArray.shape)
            phiGapFunDefined = "GapFunctionIsTurnedOF"

        return phiGapProjectedArray, phiGapFunDefined

    def getLayerMaterialProperty(self, layer, property):
        materialName = self.layUpDefinition.iloc[layer - 1, 2]
        return self.materialDatabase[materialName][property]

    def getLayerMaterial(self, layer):
        materialName = self.layUpDefinition.iloc[layer - 1, 2]
        return self.materialDatabase[materialName]

    def getSectionAngle(self, section, layer):
        return self.projectedSecAngle[layer - 1, section - 1]

    def getSectionContour(self, section):
        filterSectionHigh = self.secBordersAxial[section] >= self.interpolatedTankContourXY[:, 0]  #
        filterSectionLow = self.interpolatedTankContourXY[:, 0] > self.secBordersAxial[section - 1]
        filter = filterSectionHigh & filterSectionLow

        return self.interpolatedTankContourXY[:][filter]

    def plotContourWithSections(self, sizeText=10.0):
        numberSections = self.sections

        fig, ax = plt.subplots()
        ax.set_title("Contour With Sections")
        ax.set_xlabel("Axial [mm]")
        ax.set_ylabel("Radius[mm]")

        # Set x and y limits for your tank contour
        ax.set_xlim(self.interpolatedTankContourXY[0, 0], self.interpolatedTankContourXY[-1, 0] * 1.05)
        ax.set_ylim(0, self.interpolatedTankContourXY[0, 1] * 1.1)

        sectionsRange = range(1, numberSections + 1)
        for sec in sectionsRange:
            sectionContour = self.getSectionContour(sec)
            xSection = sectionContour[:, 0]
            ySection = sectionContour[:, 1]

            ax.plot(xSection, ySection, label="Sec-" + str(sec))

            xSectionMean = np.mean(xSection)
            ySectionMean = np.mean(ySection)
            ax.text(xSectionMean, ySectionMean, str(sec), size=sizeText)

        # activate minorticks and make the y-axis have the same scale as the x-axis
        ax.minorticks_on()
        ax.set_aspect("equal", adjustable="box")

        # Display a grid on the plot
        ax.grid(which="both")

        # save plot to PDF file with resolution of 300 DPI
        plt.savefig(os.path.join(self.saveFilesAt, "contourWithSections.pdf"), dpi=300)


if __name__ == "__main__":
    CylinderContour = np.array([[0, 850], [1000, 850]])
    DomeContour = np.array(
        [
            [
                1000,
                1205.633611,
                1425,
                1611.43883,
                1704.681937,
                1750.505454,
                1788.106276,
                1812.859043,
                1824.751367,
                1834.383106,
                1845.343611,
                1850,
            ],
            [
                850,
                824.7513673,
                736.1215932,
                590.4596149,
                475.313968,
                399.0508284,
                318.4156044,
                248.515949,
                205.6336113,
                162.1876461,
                88.84919378,
                0,
            ],
        ]
    ).transpose()

    SectionDefinition = pd.DataFrame(
        {
            "SectionNumber": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "Dome": [False, False, True, True, True, True, True, True, True, True],
            "SectionStop": [0.5, 1001, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
        }
    )

    LayUpDefinition = pd.DataFrame(
        {
            "Layer": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            "Process": [
                "IsoAngleSteering",
                "PolarPatch",
                "PolarPatch",
                "PolarPatch",
                "IsoAngleSteering",
                "IsoAngleSteering",
                "IsoAngleSteering",
                "IsoAngleSteering",
                "IsoAngleSteering",
                "IsoAngleSteering",
                "WindingStyleGeo",
                "WindingStyleGeo",
                "IsoAngSteerLimitsV1",
            ],
            "Material": [
                "Mat1",
                "Mat1",
                "Mat1",
                "Mat1",
                "Mat1",
                "Mat2",
                "Mat1",
                "Mat1",
                "Mat1",
                "Mat1",
                "Mat1",
                "Mat1",
                "Mat1",
            ],
            "Angle": [0, 45, 90, -45, 45, -45, 90, 90, 90, 90, -45, 45, 30],
        }
    )
    PolarPatchProcessParameters = {"maxRadiusRatio2RCyl": 0.6}
    IsoAngleSteeringProcessParameters = {
        "minSteeringAngle": 0.0,
        "maxSteeringAngle": 90.0,
        "defRangeStart": 0.0,
        "defRangeStop": 90.0,
        "defRangeMinPhiGap": 0.0,
        "defRangeMaxPhiGap": 0.6,
    }
    WindingStyleGeoProcessParameters = {
        "minSteeringAngle": 0.0,
        "maxSteeringAngle": 90.0,
        "defRangeStart": 0.0,
        "defRangeStop": 90.0,
        "defRangeMinPhiGap": 0.0,
        "defRangeMaxPhiGap": 0.6,
    }
    IsoAngSteerLimitsV1Parameters = {
        "steeringLimit": 1000.0,
        "defRangeStart": 0.0,
        "defRangeStop": 90.0,
        "defRangeMinPhiGap": 0.0,
        "defRangeMaxPhiGap": 0.7,
    }
    ProcessesDic = {
        "IsoAngleSteering": IsoAngleSteeringProcessParameters,
        "PolarPatch": PolarPatchProcessParameters,
        "WindingStyleGeo": WindingStyleGeoProcessParameters,
        "IsoAngSteerLimitsV1": IsoAngSteerLimitsV1Parameters,
        "CSTable": {},
    }

    LayUpDesign = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        ]
    )

    a = LayUpClass("Test", 10, SectionDefinition, CylinderContour, DomeContour)
    a.addMaterial(
        "Mat1",
        {
            "tows": 5,
            "bandWidth": 8,
            "t": 0.25,
            "phiFiber": 0.544,
            "E1": 127015,
            "E2": 9053,
            "Nu12": 0.35,
            "Nu23": 0.4,
            "G12": 5220,
            "G13": 5220,
            "G23": 3352,
            "Efiber": 229947.3461,
            "G12fiber": 4707,
            "Nu12fiber": 0.3919,
            "Nu23fiber": 0.483823529,
            "Eres": 4218,
            "G12res": 6000,
            "Nu12res": 0.3,
            "Roh": 0.000000001525,
            "Rohfiber": 0.00000000174126,
            "Rohres": 0.000000001267,
            "Xt": 1661,
            "Xc": 1396,
            "Yt": 52.9,
            "Yc": 282,
            "Sl": 159,
            "St": 86,
            "alpha0": 53,
            "psi0": 53,
            "CTE1": 0.18e-6,
            "CTE2": 30e-6,
            "CTE3": 30e-6,
        },
    )
    a.addMaterial(
        "Mat2",
        {
            "tows": 5,
            "bandWidth": 8,
            "t": 0.25,
            "phiFiber": 0.544,
            "E1": 127015,
            "E2": 9053,
            "Nu12": 0.35,
            "Nu23": 0.4,
            "G12": 5220,
            "G13": 5220,
            "G23": 3352,
            "Efiber": 229947.3461,
            "G12fiber": 4707,
            "Nu12fiber": 0.3919,
            "Nu23fiber": 0.483823529,
            "Eres": 4218,
            "G12res": 6000,
            "Nu12res": 0.3,
            "Roh": 0.000000001525,
            "Rohfiber": 0.00000000174126,
            "Rohres": 0.000000001267,
            "Xt": 1661,
            "Xc": 1396,
            "Yt": 52.9,
            "Yc": 282,
            "Sl": 159,
            "St": 86,
            "alpha0": 53,
            "psi0": 53,
            "CTE1": 0.18e-6,
            "CTE2": 30e-6,
            "CTE3": 30e-6,
        },
    )
    a.addLayUp(LayUpDefinition, LayUpDesign)
    a.processesDic = ProcessesDic
    log.info(a.getLayerMaterialProperty(6, "tows"))
    sectionContour = a.getSectionContour(10)
    # todo: maybe include this: a.simulationParameters["plotGapAndAngleFunction"] = False
    a.projectAngles()
    log.info("Projected alpha Values")
    log.info(a.projectedSecAngle)
    log.info("Projected Phi Gap Values")
    log.info(a.projectedSecPhiGap)
    a.plotContourWithSections()
    a.createAxialCoordinates2ContourLengthFunction()
    xContour = a.axialCylLengthAsAFunOfContourLength(23)
