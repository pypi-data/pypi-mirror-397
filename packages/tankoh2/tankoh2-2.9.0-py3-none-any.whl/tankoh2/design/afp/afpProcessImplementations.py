import os
from decimal import Decimal, getcontext

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline, interp1d

from tankoh2.design.afp.afpProcessClass import ProcessClass
from tankoh2.design.afp.gapVolumeContentFunction import psiGapFun


class IsoAngleSteeringProcess(ProcessClass):

    def evaluateProcess(self, x, r, angle, layerNumber, evaluationArg={}, plotDir=""):
        self.angleSignFun(angle)
        projectedAngles = self.angleProjectionFun(r, angle)
        angleFunDefined = self.definitionRangeProjectionFun(projectedAngles)
        notExceedingSteeringLimit = self.steeringLimitFun(projectedAngles)
        if plotDir:
            self.plotAndSaveProcess(
                x, r, projectedAngles, angleFunDefined, notExceedingSteeringLimit, layerNumber, plotDir
            )
        return projectedAngles, angleFunDefined, notExceedingSteeringLimit

    def angleProjectionFun(self, r, angle):
        angleProj = np.zeros(r.shape)
        angleProj[:] = angle

        return angleProj

    def definitionRangeProjectionFun(self, projectedAngles):
        angleOverMinValue = self.processPara["defRangeStart"] <= self.angleSign * projectedAngles
        angleUnderMaxValue = self.processPara["defRangeStop"] >= self.angleSign * projectedAngles
        angleFunDefined = angleOverMinValue & angleUnderMaxValue

        return angleFunDefined

    def steeringLimitFun(self, projectedAngles):
        angleOverMinValue = self.processPara["minSteeringAngle"] <= self.angleSign * projectedAngles
        angleUnderMaxValue = self.processPara["maxSteeringAngle"] >= self.angleSign * projectedAngles
        notExceedingSteeringLimit = angleOverMinValue & angleUnderMaxValue

        return notExceedingSteeringLimit

    def evaluatePhiGap(self, x, r, projectedAngles, material, layerNumber, evaluationArg={}, plotDir=""):
        phiGapProjectedArray, phiGapFunDefined = self.projectPhiGap(x, r, projectedAngles, material)
        if plotDir:
            self.plotAndSavePhiGap(x, r, phiGapProjectedArray, phiGapFunDefined, layerNumber, plotDir)
        return phiGapProjectedArray, phiGapFunDefined

    def projectPhiGap(self, axialArray, radiusArray, projectedAngles, materialLayer):
        bandWidth = materialLayer["bandWidth"]
        numberOfTows = materialLayer["tows"]

        phiGapProjectedArray, phiGapFunDefined = psiGapFun(radiusArray, projectedAngles, bandWidth, numberOfTows)

        return phiGapProjectedArray, phiGapFunDefined


class IsoAngSteerLimitsV1(ProcessClass):
    """This process applies only for the dimensions of the Tacoma Tank! It is a first Version and implements a
    function that calculates steering limits. That function was derived by DLR-SY-Stade."""

    def __init__(self, uniqueName, processParametersDic):
        self.name = uniqueName
        self.processPara = processParametersDic
        self.angleSign = +1
        self.steeringLimitPolyTab = self.loadSteeringPolynomosTable()

    def loadSteeringPolynomosTable(self):
        def convert_to_decimal(value):
            try:
                return Decimal(str(value))
            except (ValueError, TypeError):
                return value  # Return the original value if conversion fails

        getcontext().prec = 25
        dataTypes = {
            "angle": float,
            "a6": "object",  # Use 'object' as dtype and apply conversion later
            "a5": "object",
            "a4": "object",
            "a3": "object",
            "a2": "object",
            "a1": "object",
            "base": "object",
        }

        dfEx = pd.read_excel(
            os.path.join(os.path.dirname(__file__), "inputFiles", "SteeringParametersV1.xlsx"),
            sheet_name="Tabelle1",
            dtype=dataTypes,
        )

        # Apply the custom conversion function to relevant columns
        decimal_columns = ["a6", "a5", "a4", "a3", "a2", "a1", "base"]
        for col in decimal_columns:
            dfEx[col] = dfEx[col].apply(convert_to_decimal)

        return dfEx

    def evaluateProcess(self, x, r, angle, layerNumber, evaluationArg={}, plotDir=""):
        self.angleSignFun(angle)
        projectedAngles = self.angleProjectionFun(r, angle)
        angleFunDefined = self.definitionRangeProjectionFun(projectedAngles)
        notExceedingSteeringLimit = self.steeringLimitFun(x, projectedAngles[0])
        if plotDir:
            self.plotAndSaveProcess(
                x, r, projectedAngles, angleFunDefined, notExceedingSteeringLimit, layerNumber, plotDir
            )
        return projectedAngles, angleFunDefined, notExceedingSteeringLimit

    def angleProjectionFun(self, r, angle):
        angleProj = np.zeros(r.shape)
        angleProj[:] = angle

        return angleProj

    def definitionRangeProjectionFun(self, projectedAngles):
        angleOverMinValue = self.processPara["defRangeStart"] <= self.angleSign * projectedAngles
        angleUnderMaxValue = self.processPara["defRangeStop"] >= self.angleSign * projectedAngles
        angleFunDefined = angleOverMinValue & angleUnderMaxValue

        return angleFunDefined

    def steeringLimitFun(self, x, angle):
        steeringLimit = self.processPara["steeringLimit"]

        xLimit = self.xLimitFun(angle * self.angleSign, steeringLimit)

        notExceedingSteeringLimit = x <= xLimit
        return notExceedingSteeringLimit

    def xLimitFun(self, angle, steeringLimit):
        if angle < 7.5 or angle > 90.0:
            raise Exception("xLimit can not be calculated below 7.5° or above 90°")
        polynoms = self.interpolaterAllPolynomParameters(angle)
        return (
            pow(steeringLimit, 6) * polynoms[0]
            + pow(steeringLimit, 5) * polynoms[1]
            + pow(steeringLimit, 4) * polynoms[2]
            + pow(steeringLimit, 3) * polynoms[3]
            + pow(steeringLimit, 2) * polynoms[4]
            + steeringLimit * polynoms[5]
            + polynoms[6]
        )

    def interpolaterAllPolynomParameters(self, angle):
        polynoms = np.zeros((7,))

        for i, polyn in enumerate(polynoms):
            polynoms[i] = self.interpolateSinglePolynomParameter(i, angle)

        return polynoms

    def interpolateSinglePolynomParameter(self, n, angle):
        interFun = interp1d(self.steeringLimitPolyTab["angle"], self.steeringLimitPolyTab.iloc[:, n + 1])
        return interFun(angle)

    def evaluatePhiGap(self, x, r, projectedAngles, material, layerNumber, evaluationArg={}, plotDir=""):
        phiGapProjectedArray, phiGapFunDefined = self.projectPhiGap(x, r, projectedAngles, material)
        if plotDir:
            self.plotAndSavePhiGap(x, r, phiGapProjectedArray, phiGapFunDefined, layerNumber, plotDir)
        return phiGapProjectedArray, phiGapFunDefined

    def projectPhiGap(self, axialArray, radiusArray, projectedAngles, materialLayer):
        bandWidth = materialLayer["bandWidth"]
        numberOfTows = materialLayer["tows"]

        phiGapProjectedArray, phiGapFunDefined = psiGapFun(radiusArray, projectedAngles, bandWidth, numberOfTows)

        return phiGapProjectedArray, phiGapFunDefined


class CSTable(ProcessClass):
    """This process projects angles for the mode of constant steering, after IsoAngleSteering reaches its Steering
    Limits. It uses projected values from the Excel sheet "CSImport" to interpolate the projection. For values before
    the Constant Steering Range, the projection is like in IsoAngleSteering. An Exception is thrown for angles that
    are not inside the sheet."""

    def __init__(self, uniqueName, processParametersDic, filePathExcelFile):
        self.name = uniqueName
        self.processPara = processParametersDic
        self.angleSign = +1
        self.steeringTable = self.loadSteeringTable(filePathExcelFile)
        self.uniqueAnglesInTable = self.findUniqueAnglesInTable()

    def loadSteeringTable(self, filePathExelFile):
        dataTypes = {
            "Angle": float,
            "LocalAngle": float,
            "Circum Radius": float,
            "Radiant to RAL": float,
            "Radiant Dome2RAL": float,
            "RadiantPercent": float,
            "X to Dome": float,
        }
        try:
            pandasTable = pd.read_excel(filePathExelFile, sheet_name="CS_Import", dtype=dataTypes)
        except:
            raise Exception("Could not load the sheet CS_Import in the excel input file. Make sure it exists.")

        return pandasTable

    def findUniqueAnglesInTable(self):
        return self.steeringTable["Angle"].unique()

    def evaluateProcess(self, x, r, angle, layerNumber, evaluationArg={}, plotDir=""):
        self.angleSignFun(angle)
        projectedAngles = self.angleProjectionFun(
            x, angle, evaluationArg["xOffsetDomeStart"], evaluationArg["xOffsetDomeEnd"]
        )
        angleFunDefined = self.definitionRangeProjectionFun(x)
        notExceedingSteeringLimit = angleFunDefined  # same in this process
        if plotDir:
            self.plotAndSaveProcess(
                x, r, projectedAngles, angleFunDefined, notExceedingSteeringLimit, layerNumber, plotDir
            )
        return projectedAngles, angleFunDefined, notExceedingSteeringLimit

    def angleProjectionFun(self, xArray, angle, xOffsetDomeStart, xOffsetDomeEnd):
        angle = self.angleSign * angle

        self.checkIfAngleIsAUniqueValueInTheTableThrowExeceptionIfNot(angle)

        self.createInterpolationFunForAngle(angle, xOffsetDomeStart, xOffsetDomeEnd)

        angleProj = self.angleSign * self.interFunSteeringTable(xArray)

        # fill the range before the Constant Steering Range with the value of IsoAngleSteering
        IsoAngleSteeringRange = xArray <= self.xCSStart
        angleProj[IsoAngleSteeringRange] = self.angleSign * angle

        return angleProj

    def checkIfAngleIsAUniqueValueInTheTableThrowExeceptionIfNot(self, angle):
        if float(angle) in self.uniqueAnglesInTable:
            pass
        else:
            angleStrList = [str(angle) for angle in self.uniqueAnglesInTable]
            strWithAllAngles = ""
            for ang in angleStrList:
                strWithAllAngles = strWithAllAngles + ang + ", "

            raise Exception(
                "The Table contains no values for the angle "
                + str(angle)
                + ". Values exist only for the Angles: "
                + strWithAllAngles
                + " ."
            )

    def createInterpolationFunForAngle(self, absAngle, xOffsetDomeStart, xOffsetDomeEnd):
        steeringTableAngle = self.steeringTable[self.steeringTable["Angle"] == float(absAngle)]
        steeringTableAngleOrd = steeringTableAngle.sort_values(by="X to Dome", ascending=False)

        xArray = steeringTableAngleOrd["X to Dome"].to_numpy()
        xArray = (
            xOffsetDomeEnd - xOffsetDomeStart - xArray + xOffsetDomeStart
        )  # Dome length - x (dome end coordinate system) + xOffsetDomestart = x (tank coordinate system)
        LocalAngleArray = steeringTableAngleOrd["LocalAngle"].to_numpy()

        self.interFunSteeringTable = CubicSpline(xArray, LocalAngleArray, extrapolate=False)

        self.getBoundsForInterpolationFunction(xArray, xOffsetDomeStart)

    def getBoundsForInterpolationFunction(self, xArray, xOffsetDomeStart):
        self.xCSStart = xArray[0]  # Start of Constant Steering at this Position, before IsoAngleSteering
        self.xCSMax = xArray[-1]  # End of Constant Steering at this Position, SteeringLimit reached
        self.x0 = xOffsetDomeStart  # First x value of Tank Contour

    def definitionRangeProjectionFun(self, x):
        return self.xCSMax >= x

    def evaluatePhiGap(self, x, r, projectedAngles, material, layerNumber, evaluationArg={}, plotDir=""):
        phiGapProjectedArray, phiGapFunDefined = self.projectPhiGap(x, r, projectedAngles, material)
        if plotDir:
            self.plotAndSavePhiGap(x, r, phiGapProjectedArray, phiGapFunDefined, layerNumber, plotDir)
        return phiGapProjectedArray, phiGapFunDefined

    def projectPhiGap(self, axialArray, radiusArray, projectedAngles, materialLayer):
        bandWidth = materialLayer["bandWidth"]
        numberOfTows = materialLayer["tows"]

        phiGapProjectedArray, phiGapFunDefined = psiGapFun(radiusArray, projectedAngles, bandWidth, numberOfTows)

        return phiGapProjectedArray, phiGapFunDefined


class PolarPatchProcess(ProcessClass):
    def evaluateProcess(self, x, r, angle, layerNumber, evaluationArg={}, plotDir=""):
        self.angleSignFun(angle)
        projectedAngles = self.angleProjectionFun(r, angle)
        angleFunDefined = self.definitionRangeProjectionFun(r)
        notExceedingSteeringLimit = self.steeringLimitFun(r)
        if plotDir:
            self.plotAndSaveProcess(
                x, r, projectedAngles, angleFunDefined, notExceedingSteeringLimit, layerNumber, plotDir
            )
        return projectedAngles, angleFunDefined, notExceedingSteeringLimit

    def angleProjectionFun(self, r, angle):
        angleProj = np.zeros(r.shape)
        angleProj[:] = angle

        return angleProj

    def definitionRangeProjectionFun(self, r):
        rCyl = r[0]
        angleFunDefined = r <= rCyl * self.processPara["maxRadiusRatio2RCyl"]

        return angleFunDefined

    def steeringLimitFun(self, r):
        rCyl = r[0]
        notExceedingSteeringLimit = r <= rCyl * self.processPara["maxRadiusRatio2RCyl"]

        return notExceedingSteeringLimit

    def evaluatePhiGap(self, x, r, projectedAngles, material, layerNumber, evaluationArg={}, plotDir=""):
        raise Exception("The process Polar Patch doesn't have a gap function!!!")


class WindingStyleGeoProcess(ProcessClass):
    def evaluateProcess(self, x, r, angle, layerNumber, evaluationArg={}, plotDir=""):
        self.angleSignFun(angle)
        projectedAngles, funDefined = self.angleProjectionFun(r, angle)
        angleFunDefined = self.definitionRangeProjectionFun(projectedAngles, funDefined)
        notExceedingSteeringLimit = self.steeringLimitFun(projectedAngles)
        if plotDir:
            self.plotAndSaveProcess(
                x, r, projectedAngles, angleFunDefined, notExceedingSteeringLimit, layerNumber, plotDir
            )
        return projectedAngles, angleFunDefined, notExceedingSteeringLimit

    def angleProjectionFun(self, r, angle):
        rCyl = r[0]
        c = rCyl * np.sin(np.deg2rad(np.abs(angle)))
        # auclair angle
        oldErrorSettings = np.seterr(invalid="ignore")  # here it is OK to generate NANs when r>c
        localAngle = np.arcsin(c / r)
        np.seterr(invalid=oldErrorSettings["invalid"])

        filterForNan = np.isnan(localAngle)
        localAngle[filterForNan] = 0.5 * np.pi

        filterForOverC = r < c
        localAngle[filterForOverC] = 0

        funDefined = np.invert(filterForOverC)

        localAngleInDeg = np.rad2deg(localAngle)

        filterForCyl = r == rCyl
        localAngleInDeg[filterForCyl] = np.abs(angle)

        return self.angleSign * localAngleInDeg, funDefined

    def definitionRangeProjectionFun(self, projectedAngles, funDefined):
        angleOverMinValue = self.processPara["defRangeStart"] <= self.angleSign * projectedAngles
        angleUnderMaxValue = self.processPara["defRangeStop"] >= self.angleSign * projectedAngles
        angleFunDefined = angleOverMinValue & angleUnderMaxValue & funDefined

        return angleFunDefined

    def steeringLimitFun(self, projectedAngles):
        angleOverMinValue = self.processPara["minSteeringAngle"] <= self.angleSign * projectedAngles
        angleUnderMaxValue = self.processPara["maxSteeringAngle"] >= self.angleSign * projectedAngles
        notExceedingSteeringLimit = angleOverMinValue & angleUnderMaxValue

        return notExceedingSteeringLimit

    def evaluatePhiGap(self, x, r, projectedAngles, material, layerNumber, evaluationArg={}, plotDir=""):
        phiGapProjectedArray, phiGapFunDefined = self.projectPhiGap(x, r, projectedAngles, material)
        if plotDir:
            self.plotAndSavePhiGap(x, r, phiGapProjectedArray, phiGapFunDefined, layerNumber, plotDir)
        return phiGapProjectedArray, phiGapFunDefined

    def projectPhiGap(self, axialArray, radiusArray, projectedAngles, materialLayer):
        bandWidth = materialLayer["bandWidth"]
        numberOfTows = materialLayer["tows"]

        phiGapProjectedArray, phiGapFunDefined = psiGapFun(radiusArray, projectedAngles, bandWidth, numberOfTows)

        return phiGapProjectedArray, phiGapFunDefined
