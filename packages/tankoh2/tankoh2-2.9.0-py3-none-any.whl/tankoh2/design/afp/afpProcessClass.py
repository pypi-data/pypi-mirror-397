import os

import matplotlib.pyplot as plt
import numpy as np

from tankoh2.design.afp.gapVolumeContentFunction import psiGapFun


class ProcessClass:
    def __init__(self, uniqueName, processParametersDic):
        self.name = uniqueName
        self.processPara = processParametersDic
        self.angleSign = +1

    def evaluateProcess(self, x, r, angle, material, layerNumber, evaluationArg={}, plotDir=""):
        self.angleSignFun(angle)
        projectedAngles = self.angleProjectionFun(r, angle, material)
        angleFunDefined = self.definitionRangeProjectionFun(projectedAngles, material)
        notExceedingSteeringLimit = self.steeringLimitFun(r, projectedAngles, material)
        if plotDir:
            self.plotAndSaveProcess(
                x, r, projectedAngles, angleFunDefined, notExceedingSteeringLimit, layerNumber, plotDir
            )
        return projectedAngles, angleFunDefined, notExceedingSteeringLimit

    def angleSignFun(self, angle):
        if angle < 0:
            self.angleSign = -1
        else:
            self.angleSign = +1

    def angleProjectionFun(self, r, angle, material):
        rCyl = r[0]
        rPolOpen = r[-1]

        return angle * ((r - rPolOpen) / (rCyl - rPolOpen)) + self.angleSign * np.rad2deg(
            np.arccos(((r - rPolOpen) / (rCyl - rPolOpen)))
        )

    def definitionRangeProjectionFun(self, projectedAngles, material):
        rangeMinAngle = self.processPara["defRangeMinAngle"]
        rangeMaxAngle = self.processPara["defRangeMaxAngle"]

        angleOverMinValue = rangeMinAngle <= self.angleSign * projectedAngles
        angleUnderMaxValue = rangeMaxAngle >= self.angleSign * projectedAngles
        angleFunDefined = angleOverMinValue & angleUnderMaxValue

        return angleFunDefined

    def steeringLimitFun(self, r, projectedAngles, material):
        rCyl = r[0]
        relativeSteeringLimit = self.processPara["relativeSteeringLimit"]

        SteeringLimit = relativeSteeringLimit * rCyl
        notExceedingSteeringLimit = self.angleSign * projectedAngles <= SteeringLimit

        return notExceedingSteeringLimit

    def evaluatePhiGap(self, x, r, projectedAngles, material, layerNumber, evaluationArg={}, plotDir=""):
        phiGapProjectedArray = self.projectPhiGap(x, r, projectedAngles, material)
        phiGapFunDefined = self.definitionRangeGapFun(phiGapProjectedArray, material)
        if plotDir:
            self.plotAndSavePhiGap(x, r, phiGapProjectedArray, phiGapFunDefined, layerNumber, plotDir)
        return phiGapProjectedArray, phiGapFunDefined

    def projectPhiGap(self, axialArray, radiusArray, projectedAngles, materialLayer):
        bandWidth = materialLayer["bandWidth"]
        numberOfTows = materialLayer["tows"]

        phiGapProjectedArray, _ = psiGapFun(radiusArray, projectedAngles, bandWidth, numberOfTows)

        return phiGapProjectedArray

    def definitionRangeGapFun(self, phiGapProjectedArray, material):
        rangeMinPhiGap = self.processPara["defRangeMinPhiGap"]
        rangeMaxPhiGap = self.processPara["defRangeMaxPhiGap"]

        phiGapOverMinValue = rangeMinPhiGap <= phiGapProjectedArray
        angleUnderMaxValue = rangeMaxPhiGap >= phiGapProjectedArray
        phiGapFunDefined = phiGapOverMinValue & angleUnderMaxValue

        return phiGapFunDefined

    def plotAndSaveProcess(
        self, x, r, projectedAngles, angleFunDefined, notExceedingSteeringLimit, layerNumber, runDir
    ):
        # Create a figure with 5 subplots
        fig, axes = plt.subplots(5, 1, figsize=(8, 14))  # Adjust figsize as needed

        # Plot x over index
        axes[0].plot(range(len(x)), x)
        axes[0].set_title("Axial Position")
        axes[0].set_xlabel("Index")
        axes[0].set_ylabel("Axial Position[mm]")

        # Plot radius over index
        axes[1].plot(range(len(r)), r)
        axes[1].set_title("Radius")
        axes[1].set_xlabel("Index")
        axes[1].set_ylabel("Radius[mm]")

        # Plot projectedAngles
        axes[2].plot(range(len(projectedAngles)), projectedAngles)
        axes[2].set_title("Projected Angles Layer " + str(layerNumber))
        axes[2].set_xlabel("Index")
        axes[2].set_ylabel("Angle[°]")

        # Plot angleFunDefined
        axes[3].plot(range(len(angleFunDefined)), [int(val) for val in angleFunDefined], linestyle="--")
        axes[3].set_title("Angle Function Defined for Layer " + str(layerNumber))
        axes[3].set_xlabel("Index")
        axes[3].set_ylabel("Defined[boolean]")
        axes[3].set_yticks([0, 1], ["False", "True"])

        # Plot exceedingSteeringLimit
        axes[4].plot(
            range(len(notExceedingSteeringLimit)), [int(val) for val in notExceedingSteeringLimit], linestyle="--"
        )
        axes[4].set_title("Not Exceeding Steering Limit for Layer " + str(layerNumber))
        axes[4].set_xlabel("Index")
        axes[4].set_ylabel("Not Exceeded[boolean]")
        axes[4].set_yticks([0, 1], ["False", "True"])

        # Adjust layout for better spacing
        plt.tight_layout()

        # Save the figure
        filePath = os.path.join(runDir, "AngleFunctionLayer" + str(layerNumber) + "Contour" + ".png")

        plt.savefig(filePath)
        # plt.show()

        # Create a figure with 4 subplots
        fig, axes = plt.subplots(4, 1, figsize=(8, 12))  # Adjust figsize as needed

        # Plot radius over x
        axes[0].plot(x, r)
        axes[0].set_title("Radius")
        axes[0].set_xlabel("Axial Position[mm]")
        axes[0].set_ylabel("Radius[mm]")

        # Plot projectedAngles
        axes[1].plot(x, projectedAngles)
        axes[1].set_title("Projected Angles Layer " + str(layerNumber))
        axes[1].set_xlabel("Axial Position[mm]")
        axes[1].set_ylabel("Angle[°]")

        # Plot angleFunDefined
        axes[2].plot(x, [int(val) for val in angleFunDefined], linestyle="--")
        axes[2].set_title("Angle Function Defined for Layer " + str(layerNumber))
        axes[2].set_xlabel("Axial Position[mm]")
        axes[2].set_ylabel("Defined[boolean]")
        axes[2].set_yticks([0, 1], ["False", "True"])

        # Plot exceedingSteeringLimit
        axes[3].plot(x, [int(val) for val in notExceedingSteeringLimit], linestyle="--")
        axes[3].set_title("Not Exceeding Steering Limit for Layer " + str(layerNumber))
        axes[3].set_xlabel("Axial Position[mm]")
        axes[3].set_ylabel("Not Exceeded[boolean]")
        axes[3].set_yticks([0, 1], ["False", "True"])

        # Adjust layout for better spacing
        plt.tight_layout()

        # Save the figure

        filePath = os.path.join(runDir, "AngleFunctionLayer" + str(layerNumber) + "XPos" + ".png")

        plt.savefig(filePath)
        # plt.show()

    def plotAndSavePhiGap(self, x, r, projectedPhiGap, phiGapFunDefined, layerNumber, plotDir):
        # Create a figure with 5 subplots
        fig, axes = plt.subplots(4, 1, figsize=(8, 14))  # Adjust figsize as needed

        # Plot x over index
        axes[0].plot(range(len(x)), x)
        axes[0].set_title("Axial Position")
        axes[0].set_xlabel("Index")
        axes[0].set_ylabel("Axial Position[mm]")

        # Plot radius over index
        axes[1].plot(range(len(r)), r)
        axes[1].set_title("Radius")
        axes[1].set_xlabel("Index")
        axes[1].set_ylabel("Radius[mm]")

        # Plot projected phis
        axes[2].plot(range(len(projectedPhiGap)), projectedPhiGap)
        axes[2].set_title("Projected Phi Gap Layer " + str(layerNumber))
        axes[2].set_xlabel("Index")
        axes[2].set_ylabel("Phi Gap[%]")

        # Plot phiFunDefined
        axes[3].plot(range(len(phiGapFunDefined)), [int(val) for val in phiGapFunDefined], linestyle="--")
        axes[3].set_title("Phi Gap Function Defined for Layer " + str(layerNumber))
        axes[3].set_xlabel("Index")
        axes[3].set_ylabel("Defined[boolean]")
        axes[3].set_yticks([0, 1], ["False", "True"])

        # Adjust layout for better spacing
        plt.tight_layout()

        # Save the figure
        filePath = os.path.join(plotDir, "GapFunctionLayer" + str(layerNumber) + "Contour" + ".png")
        plt.savefig(filePath)
        # plt.show()

        # Create a figure with 4 subplots
        fig, axes = plt.subplots(3, 1, figsize=(8, 12))  # Adjust figsize as needed

        # Plot radius over x
        axes[0].plot(x, r)
        axes[0].set_title("Radius")
        axes[0].set_xlabel("Axial Position[mm]")
        axes[0].set_ylabel("Radius[mm]")

        # Plot projectedAngles
        axes[1].plot(x, projectedPhiGap)
        axes[1].set_title("Projected Phi Gap for Layer " + str(layerNumber))
        axes[1].set_xlabel("Axial Position[mm]")
        axes[1].set_ylabel("Phi Gap[%]")

        # Plot angleFunDefined
        axes[2].plot(x, [int(val) for val in phiGapFunDefined], linestyle="--")
        axes[2].set_title("Phi Gap Function Defined for Layer " + str(layerNumber))
        axes[2].set_xlabel("Axial Position[mm]")
        axes[2].set_ylabel("Defined[boolean]")
        axes[2].set_yticks([0, 1], ["False", "True"])

        # Adjust layout for better spacing
        plt.tight_layout()

        # Save the figure
        filePath = os.path.join(plotDir, "GapFunctionLayer" + str(layerNumber) + "XPos" + ".png")
        plt.savefig(filePath)
        # plt.show()
