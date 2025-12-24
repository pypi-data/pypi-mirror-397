import os
import pickle

import numpy as np
import pandas as pd
from bokeh.models import Legend, Span, TabPanel, Tabs, Text
from bokeh.models.sources import ColumnDataSource
from bokeh.palettes import Category20
from bokeh.plotting import figure, output_file, save


class ResultsObj:
    def __init__(self, layUp, nodesDicWithResults, angleContourNodesDic, allNodesDF, elements2NodesDic):
        self.nodesWithResultsDic = nodesDicWithResults
        self.angleContourNodesDic = angleContourNodesDic
        self.nodesDF = allNodesDF
        self.elements2NodesDic = elements2NodesDic
        self.LayUpIns = layUp
        self.createPandasDf()

    def createPandasDf(self):
        self.invertElements2NodesDic()
        rows = []

        for angle, nodeRange in self.angleContourNodesDic.items():
            for node in nodeRange:
                try:
                    nodeDic = self.nodesWithResultsDic[node]
                    uDic = nodeDic["U"]
                    layerKeys = [layer for layer in nodeDic.keys() if layer != "U"]
                    x, y, z = self.obtainPostionalInformation(node)
                    self.LayUpIns.createAxialCoordinates2ContourLengthFunction()

                    xContour = self.LayUpIns.contourLengthAsFunOfAxialPosition(x)

                    for layer in layerKeys:
                        row = self.createValueRow(angle, layer, node, uDic, nodeDic[layer], x, y, z, xContour)
                        rows.append(row)
                except:
                    print("Could not find node {} in result data retrieved from odb.".format(node))

        self.resultsDF = pd.DataFrame(rows)

    def obtainPostionalInformation(self, node):
        row = self.nodesDF.iloc[node - 1]
        x = row["x"]
        y = row["y"]
        z = row["z"]
        return x, y, z

    def invertElements2NodesDic(
        self,
    ):
        self.nodes2elementDic = {}
        for element in self.elements2NodesDic.keys():
            for node in self.elements2NodesDic[element]["nodes"]:
                self.nodes2elementDic[node] = {
                    "element": element,
                    "section": self.elements2NodesDic[element]["section"],
                }

    def createValueRow(self, angle, layer, node, uDic, layerDic, x, y, z, xContour):
        return {
            "AngleContour [°]": angle,
            "Layer": layer,
            "Section": self.nodes2elementDic[node]["section"],
            "Node": node,
            "Corresponding Element": self.nodes2elementDic[node]["element"],
            "Contour [mm]": float(xContour),
            "x [mm]": x,
            "y [mm]": y,
            "z [mm]": z,
            "U1": uDic["U1"],
            "U2": uDic["U2"],
            "U3": uDic["U3"],
            "U_magnitude": uDic["magnitude"],
            "LE11": layerDic["LE"]["LE11"] * 100,
            "LE22": layerDic["LE"]["LE22"] * 100,
            "S11": layerDic["S"]["S11"],
            "S22": layerDic["S"]["S22"],
            "S12": layerDic["S"]["S12"],
            "LarcFkCrt": layerDic["LarcFkCrt"],
            "LarcFsCrt": layerDic["LarcFsCrt"],
            "LarcFtCrt": layerDic["LarcFtCrt"],
            "LarcMcCrt": layerDic["LarcMcCrt"],
        }

    def exportAll2Excel(self, runDir):
        self.resultsDF.to_excel(os.path.join(runDir, "results.xlsx"))

    def plotAsHTML(self, runDir):
        # Set  up file in folder
        output_file(
            filename=os.path.join(runDir, "ResultPlots.html"),
            title="Layer Results for Contour",
        )

        contourLines = self.resultsDF["AngleContour [°]"].unique()

        tabsList = []
        for contourLine in contourLines:
            tabsList.append(TabPanel(child=self.plotAngle(contourLine), title="Con. " + str(contourLine) + "°"))

        tabs0 = Tabs(tabs=tabsList)

        save(tabs0)

    def plotAngle(self, angle):
        # create tabs
        tabs1 = Tabs(
            tabs=[
                TabPanel(child=self.plotAngleVal(angle, "S11"), title="S11"),
                TabPanel(child=self.plotAngleVal(angle, "S22"), title="S22"),
                TabPanel(child=self.plotAngleVal(angle, "S12"), title="S12"),
                TabPanel(child=self.plotAngleVal(angle, "LarcMcCrt"), title="LarcMcCrt"),
                TabPanel(child=self.plotAngleVal(angle, "LarcFtCrt"), title="LarcFtCrt"),
                TabPanel(child=self.plotAngleVal(angle, "LE11"), title="LE11"),
                TabPanel(child=self.plotAngleVal(angle, "LE22"), title="LE22"),
                TabPanel(child=self.plotAngleVal(angle, "U_magnitude"), title="U_magnitude"),
                TabPanel(child=self.plotAngleVal(angle, "U1"), title="U1"),
                TabPanel(child=self.plotAngleVal(angle, "U2"), title="U2"),
                TabPanel(child=self.plotAngleVal(angle, "U3"), title="U3"),
            ]
        )

        return tabs1

    def plotAngleVal(self, angle, value):
        "Configuration-------------------------------------------------------------------------------------------------"
        #  Section Lines
        fontSizeSectionText = "10pt"
        sectionTextColor = "grey"
        yPosSecText2MaxYValue = 0.9
        sectionLineColor = "grey"

        # Result Lines
        lineWidthResult = 3

        # Legend
        legendColumns = 9
        legendLabelWidth = 18
        legendLineWidth = 18
        legendLabelFontSize = "8pt"
        legendBorderLineWidth = 2
        legendLineColor = "black"

        # Figure
        figureHeight = 600
        figureWidth = 800
        backGroundFillColor = "white"
        axisTickSize = "14pt"
        axisTextsize = "12pt"
        titleFontSize = "18pt"

        value2YAxisLabel = {
            "U1": "Deformation along x, U1 [mm]",
            "U2": "Deformation along y, U2 [mm]",
            "U3": "Deformation along z, U3 [mm]",
            "U_magnitude": "Total deformation, U [mm]",
            "LE11": "Strain along the fiber, 1‑axis [%]",
            "LE22": "Strain transverse to fiber, 2‑axis [%]",
            "S11": "Stress along fiber, S11 [N/mm2]",
            "S22": "Stress transverse to fiber, S22 [N/mm2]",
            "S12": "In-Plane shear, S12 [N/mm2]",
            "LarcFkCrt": "Fiber kinking",
            "LarcFsCrt": "Fiber split",
            "LarcFtCrt": "Fiber tensile",
            "LarcMcCrt": "Matrix cracking",
        }

        "Method Internal Functions-------------------------------------------------------------------------------------"

        def insertSectionBorderVLines():
            sectionBordersAxial = self.LayUpIns.secBordersAxial
            sectionBordersContour = self.LayUpIns.contourLengthAsFunOfAxialPosition(sectionBordersAxial)

            secAxisTicks = []
            secAxisLabels = []

            # Vertical Lines
            for secIndex, xSecContour in enumerate(sectionBordersContour):
                secAxisTicks.append(xSecContour)
                secAxisLabels.append(str(secIndex))
                vLine = Span(location=xSecContour, dimension="height", line_color=sectionLineColor)
                p.add_layout(vLine)

            return secAxisTicks, secAxisLabels

        def maxValueOfSelectedResult():
            return self.resultsDF[value].max()

        def plotTextDesInEverySection(secAxisTicks, secAxisLabels, maxYValue):
            xPosText = []
            yPosText = []
            yPostion = maxYValue * yPosSecText2MaxYValue

            secAxisLabels = secAxisLabels[1:]  # section 0 will not be plotted, as it not exists
            secAxisLabels = ["Sec. " + label for label in secAxisLabels]
            for i, label in enumerate(secAxisLabels):
                xPos = 0.5 * (secAxisTicks[i] + secAxisTicks[i + 1])
                xPosText.append(xPos)
                yPosText.append(yPostion)

            textSource = ColumnDataSource(dict(xText=xPosText, yText=yPosText, posLabel=secAxisLabels))

            textGlyph = Text(
                x="xText",
                y="yText",
                text="posLabel",
                angle=np.pi / 2,
                text_color=sectionTextColor,
                text_align="center",
                text_font_size={"value": fontSizeSectionText},
            )

            p.add_glyph(textSource, textGlyph)

        def plotAllPlies():
            renderers = []

            for i, layer in enumerate(layers):
                layerSubSet = sortedDF[sortedDF["Layer"] == layer]
                layerSource = ColumnDataSource(
                    dict(
                        value=layerSubSet[value],
                        contour=layerSubSet["Contour [mm]"],
                        layer=layerSubSet["Layer"],
                        x=layerSubSet["x [mm]"],
                        z=layerSubSet["z [mm]"],
                        y=layerSubSet["y [mm]"],
                    )
                )
                r = p.line(
                    "contour",
                    "value",
                    source=layerSource,
                    line_width=lineWidthResult,
                    line_color=colors[i % differentColors],
                )
                renderers.append(r)
            return renderers

        def createLegend(renderers):
            legend_items = []
            for i, layer in enumerate(layers):
                angleStr = str(self.LayUpIns.layUpDefinition.iloc[int(layer) - 1, 3])
                item = ("L" + str(i + 1) + "_A" + angleStr, [renderers[i]])
                legend_items.append(item)

            nRows = len(layers) // 6

            custom_legend = Legend(
                items=legend_items,
                location="center_left",
                orientation="horizontal",
                ncols=legendColumns,
                nrows="auto",
                label_width=legendLabelWidth,
                glyph_width=legendLineWidth,
                spacing=2,
                margin=2,
            )

            p.add_layout(custom_legend, "below")
            p.legend.click_policy = "hide"

            p.legend.label_text_font_size = legendLabelFontSize
            p.legend.border_line_color = legendLineColor
            p.legend.border_line_width = legendBorderLineWidth

        "Method Workflow-----------------------------------------------------------------------------------------------"
        # Select relevant SubDF
        angleDF = self.resultsDF[self.resultsDF["AngleContour [°]"] == angle]
        sortedDF = angleDF.sort_values(by="Contour [mm]")
        layers = [layer for layer in sorted(sortedDF["Layer"].unique())]

        # Line Colors
        differentColors = len(layers)
        if differentColors > 20:
            differentColors = 20
        colors = Category20[differentColors]

        # Create Plot
        TOOLS = "hover,pan,wheel_zoom,box_zoom,reset,save"

        titleDic = {
            "U1": "Deformation",
            "U2": "Deformation",
            "U3": "Deformation",
            "U_magnitude": "Deformation",
            "LE11": "Strain",
            "LE22": "Strain",
            "S11": "Stress",
            "S22": "Stress",
            "S12": "Stress",
            "LarcFkCrt": "LaRC05 Failure Criteria",
            "LarcFsCrt": "LaRC05 Failure Criteria",
            "LarcFtCrt": "LaRC05 Failure Criteria",
            "LarcMcCrt": "LaRC05 Failure Criteria",
        }

        p = figure(
            tools=TOOLS,
            toolbar_location="below",
            title="Layerwise " + titleDic[value] + " Results for Contour " + str(angle) + "°",
            x_axis_label="Path along the contour [mm]",
            y_axis_label=value2YAxisLabel[value],
            height=figureHeight,
            width=figureWidth,
            background_fill_color=backGroundFillColor,
            x_range=(0, self.resultsDF["Contour [mm]"].max()),
        )

        p.hover.tooltips = [
            (value2YAxisLabel[value], "@value"),
            ("Contour [mm]", "@contour"),
            ("Layer", "@layer"),
            ("x [mm]", "@x"),
            ("y [mm]", "@y"),
            ("z [mm]", "@z"),
        ]

        p.xaxis.minor_tick_line_width = 0
        p.yaxis.minor_tick_line_width = 0

        # Set font size of axis ticks
        p.xaxis.major_label_text_font_size = axisTextsize
        p.yaxis.major_label_text_font_size = axisTextsize

        # Set font size of axis labels
        p.xaxis.axis_label_text_font_size = axisTickSize
        p.yaxis.axis_label_text_font_size = axisTickSize

        p.title.text_font_size = titleFontSize

        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None

        p.outline_line_color = None

        # Vertical lines to display section borders
        secAxisTicks, secAxisLabels = insertSectionBorderVLines()
        maxYValue = maxValueOfSelectedResult()
        plotTextDesInEverySection(secAxisTicks, secAxisLabels, maxYValue)

        # Plot values for all plies
        renderers = plotAllPlies()

        # Create Legend
        createLegend(renderers)

        # Return
        return p


def plotAndSaveFilesAndObj(resultsObjIns, runDir):
    # export to excel
    resultsObjIns.exportAll2Excel(runDir)
    # Plot all results for all contour Lines as HTML
    resultsObjIns.plotAsHTML(runDir)
    # save resultsObjIns as pickle
    saveAt = resultsObjIns.LayUpIns.saveFilesAt
    with open(os.path.join(saveAt, "resultsObjIns.pkl"), "wb") as fp:
        pickle.dump(resultsObjIns, fp)
