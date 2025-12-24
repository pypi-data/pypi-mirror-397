import numpy as np
import regionToolset
from abaqus import *
from abaqusConstants import *
from part import *

"Import Functions------------------------------------------------------------------------------------------------------"

"Create Geometry Functions---------------------------------------------------------------------------------------------"


def createTankGeoOpenPolar(my_model, cyCoordinates, domeCoordinates, radiusChangeInCyl, tank360=True):
    if tank360:
        sweepAngle = 360
        partName = "AFP360Tank"
    else:
        sweepAngle = 90
        partName = "AFP1/4Tank"

    onlyDomeFlag = checkIfOnlyDome(radiusChangeInCyl)

    # Value Import
    if not onlyDomeFlag:
        contourPointsCyl = getCylPoints(cyCoordinates)
    contourPointsDome = getDomePoints(domeCoordinates)

    mySketch = my_model.ConstrainedSketch(name="__profile__", sheetSize=contourPointsDome[0][1] * 3)
    g, v, d, c = mySketch.geometry, mySketch.vertices, mySketch.dimensions, mySketch.constraints
    # Creating the construction lines
    mySketch.setPrimaryObject(option=STANDALONE)
    mySketch.ConstructionLine(point1=(-contourPointsDome[0][1] * 2, 0.0), point2=(contourPointsDome[0][1] * 2, 0.0))
    mySketch.FixedConstraint(entity=g.findAt((0.0, 0.0)))

    # Sketch Contour
    if not onlyDomeFlag:
        drawCylLines(mySketch, contourPointsCyl)

    mySketch.Spline(points=contourPointsDome)
    mySketch.unsetPrimaryObject()

    my_model.Part(name=partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p = my_model.parts[partName]
    p.BaseShellRevolve(sketch=mySketch, angle=sweepAngle, flipRevolveDirection=OFF)

    p = my_model.parts[partName]

    del my_model.sketches["__profile__"]

    return my_model.parts[partName]


def checkIfOnlyDome(radiusChangeInCyl):
    if len(radiusChangeInCyl) == 0:
        return True
    else:
        return False


def getDomePoints(domeCoordinates):
    contourPoints = [(element[0], element[1]) for element in domeCoordinates]

    return tuple(contourPoints)


def getCylPoints(cyCoordinates):
    pointlst = [(element[0], element[1]) for element in cyCoordinates]

    return pointlst


def drawCylLines(mySketch, cYCoordinates):
    Point1 = cYCoordinates[0]
    pointList = cYCoordinates[1:]
    for Point2 in pointList:
        mySketch.Line(point1=Point1, point2=Point2)
        Point1 = Point2


"Create Datum Functions------------------------------------------------------------------------------------------------"


def createAxialAndPolarDatum(myPart, axialLength):
    createCartesianDatum(myPart, "Datum-Axial", (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    createCylindricalDatum(myPart, "Datum-PolarPatch", (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0))
    createCylindricalDatum(myPart, "Datum-Cylindrical", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def createCartesianDatum(myPart, name, origin, xVector, yVector):
    myPart.DatumCsysByThreePoints(name=name, coordSysType=CARTESIAN, origin=origin, point1=xVector, line2=yVector)


def createCylindricalDatum(myPart, name, origin, xVector, yVector):
    myPart.DatumCsysByThreePoints(name=name, coordSysType=CYLINDRICAL, origin=origin, point1=xVector, line2=yVector)


def createDatumPlanesXZandXYplane(myPart):
    myPart.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=0.0)
    myPart.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=0.0)


"Create Sets Functions-------------------------------------------------------------------------------------------------"


def createSetsQuarterTank(part, partionBorderPoints):
    e = part.edges
    s = part.faces

    symmXEdge = getEdge(e, partionBorderPoints[0], 45)
    part.Set(edges=symmXEdge, name="symmX")

    symmYEdgeCyl = getEdge(e, partionBorderPoints[1], 0)
    symmYEdgeDome = getEdge(e, partionBorderPoints[4], 0)
    part.Set(edges=(symmYEdgeCyl, symmYEdgeDome), name="symmZ")

    symmZEdgeCyl = getEdge(e, partionBorderPoints[1], 90)
    symmZEdgeDome = getEdge(e, partionBorderPoints[4], 90)
    part.Set(edges=(symmZEdgeCyl, symmZEdgeDome), name="symmY")

    pressureSurfaceCyl = getSurface(s, partionBorderPoints[1], 45)
    pressureSurfaceDome = getSurface(s, partionBorderPoints[4], 45)

    part.Surface(
        side1Faces=(
            pressureSurfaceCyl,
            pressureSurfaceDome,
        ),
        name="innerTankInsideSurf",
    )


def createSets360Tank(part, partionBorderPoints):
    e = part.edges
    s = part.faces

    cylinderStartEdge = getEdge(e, partionBorderPoints[0], 45)
    part.Set(edges=cylinderStartEdge, name="cylStartEdge")

    pressureSurfaceCyl = getSurface(s, partionBorderPoints[1], 45)
    pressureSurfaceDome = getSurface(s, partionBorderPoints[4], 45)

    part.Surface(
        side2Faces=(
            pressureSurfaceCyl,
            pressureSurfaceDome,
        ),
        name="innerTankInsideSurf",
    )

    # createSetsForResultsContour(part, partionBorderPoints)
    createSetForTemperatureField(part, partionBorderPoints)


def createSetForTemperatureField(part, partionBorderPoints):
    f = part.faces
    faceCyl = getSurface(f, partionBorderPoints[1], 45)
    faceDome = getSurface(f, partionBorderPoints[4], 45)

    part.Set(
        faces=(
            faceCyl,
            faceDome,
        ),
        name="Set-Thermal",
    )


def createSetsForResultsContour(part, partionBorderPoints):
    e = part.edges

    EdgeCyl = getEdge(e, partionBorderPoints[1], 0)
    EdgeDome = getEdge(e, partionBorderPoints[4], 0)
    part.Set(edges=(EdgeCyl, EdgeDome), name="Contour0Deg")


def getEdge(edge, contourPoint, angle):
    pointOnEdge = getClosesdPointOnEdge(edge, contourPoint, angle)
    return edge.findAt((pointOnEdge,))


def getClosesdPointOnEdge(edge, contourPoint, angle):
    rotatedPoint = (
        contourPoint[0],
        contourPoint[1] * np.cos(np.deg2rad(angle)),
        contourPoint[1] * np.sin(np.deg2rad(angle)),
    )

    r = edge.getClosest(coordinates=(rotatedPoint,))
    return r[0][1]


def getSurface(surface, contourPoint, angle):
    rotatedPoint = (
        contourPoint[0],
        contourPoint[1] * np.cos(np.deg2rad(angle)),
        contourPoint[1] * np.sin(np.deg2rad(angle)),
    )

    r = surface.getClosest(coordinates=(rotatedPoint,))

    return surface.findAt((r[0][1],))


"Import Materials Funtions---------------------------------------------------------------------------------------------"


def createAllMaterials(myModel, matDatabase, homMatDatabase, refTemperature):
    keysMatDatabase = createMaterialsFromMatDatabase(myModel, matDatabase, refTemperature)
    createMatFromHomMatDatabase(myModel, homMatDatabase, keysMatDatabase, refTemperature)


def createMaterialsFromMatDatabase(myModel, matDatabase, refTemperature):
    keysMatDatabase = matDatabase.keys()
    keysMatDatabase = [
        str(key) for key in keysMatDatabase
    ]  # without this step abq Python does not consider it as string
    for key in keysMatDatabase:
        createLaminaMat(
            myModel,
            key,
            matDatabase[key]["E1"],
            matDatabase[key]["E2"],
            matDatabase[key]["Nu12"],
            matDatabase[key]["G12"],
            matDatabase[key]["G13"],
            matDatabase[key]["G23"],
            matDatabase[key]["Roh"],
            matDatabase[key]["Xt"],
            matDatabase[key]["Xc"],
            matDatabase[key]["Yt"],
            matDatabase[key]["Yc"],
            matDatabase[key]["Sl"],
            matDatabase[key]["alpha0"],
            matDatabase[key]["psi0"],
            matDatabase[key]["St"],
            matDatabase[key]["CTE1"],
            matDatabase[key]["CTE2"],
            matDatabase[key]["CTE3"],
            refTemperature,
        )
    return keysMatDatabase


def createMatFromHomMatDatabase(myModel, homMatDatabase, keysMatDatabase, refTemperature):
    keyHomsMatDatabase = homMatDatabase.keys()
    keyHomsMatDatabase = [
        str(key) for key in keyHomsMatDatabase
    ]  # without this step abq Python does not consider it as string
    keyHomsMatDatabaseFilter = [key for key in keyHomsMatDatabase if homMatDatabase[key] not in keysMatDatabase]
    for key in keyHomsMatDatabaseFilter:
        createLaminaMat(
            myModel,
            key,
            homMatDatabase[key]["E1"],
            homMatDatabase[key]["E2"],
            homMatDatabase[key]["Nu12"],
            homMatDatabase[key]["G12"],
            homMatDatabase[key]["G13"],
            homMatDatabase[key]["G23"],
            homMatDatabase[key]["Roh"],
            homMatDatabase[key]["Xt"],
            homMatDatabase[key]["Xc"],
            homMatDatabase[key]["Yt"],
            homMatDatabase[key]["Yc"],
            homMatDatabase[key]["Sl"],
            homMatDatabase[key]["alpha0"],
            homMatDatabase[key]["psi0"],
            homMatDatabase[key]["St"],
            homMatDatabase[key]["CTE1"],
            homMatDatabase[key]["CTE2"],
            homMatDatabase[key]["CTE3"],
            refTemperature,
        )


def createLaminaMat(
    myModel,
    nameMaterial,
    e11,
    e22,
    nu12,
    g12,
    g13,
    g23,
    roh,
    Xt,
    Xc,
    Yt,
    Yc,
    Sl,
    alpha0,
    psi0,
    St,
    CTE1,
    CTE2,
    CTE3,
    refTemperature,
):
    myModel.Material(description=nameMaterial, name=nameMaterial)
    myModel.materials[nameMaterial].Elastic(table=((e11, e22, nu12, g12, g13, g23),), type=LAMINA)
    myModel.materials[nameMaterial].Density(table=((roh,),))
    myModel.materials[nameMaterial].LaRC05DamageInitiation(table=((Xt, Xc, Yt, Yc, Sl, alpha0, psi0, St, 0.0, 0.0),))
    myModel.materials[nameMaterial].Expansion(type=ORTHOTROPIC, table=((CTE1, CTE2, CTE3),), zero=refTemperature)


"Create Partions Functions---------------------------------------------------------------------------------------------"


def createPartions(myPart, partionAtPoints, indexFirstDatumPlane, radiusChangeInCyl):
    """
    :param myPart:
    :param partionAtPoints: A list of points on the surface of the tank. For every point between the first and the last
    point a partion will be created.
    :return:
    """

    # Create Datum Planes to separate the part later into partitions
    DatumPlaneAt = partionAtPoints[1:-1]
    for border in DatumPlaneAt:
        myPart.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=border[0])

    # Get Points on every Section
    f = myPart.faces
    pointsNearSurf = pointsNearSurfaceOnSections(partionAtPoints)
    pointsOnFace = f.getClosest(coordinates=pointsNearSurf)
    keysPointsOnFace = list(pointsOnFace.keys())
    # firstPoint = pointsOnFace[keysPointsOnFace[0]][1]
    # keysPointsOnFace = keysPointsOnFace[1:]

    # Start of the partition loop
    secIndex = 0
    datumIndex = indexFirstDatumPlane
    print(radiusChangeInCyl)
    print("Beginn Cylinder Loop")
    # Partition the cylinder, if cylinder is there
    if len(radiusChangeInCyl) != 0:
        # Cylinder is there
        firstPoint = pointsOnFace[secIndex][1]
        for changeInCyl in radiusChangeInCyl:
            secondPoint = pointsOnFace[secIndex + 1][1]
            print(secIndex)
            print(datumIndex)
            print(firstPoint)
            print(secondPoint)
            if not changeInCyl:
                pickedFaces = f.findAt((firstPoint, secondPoint))
                d = myPart.datums[datumIndex]
                myPart.PartitionFaceByDatumPlane(datumPlane=d, faces=pickedFaces)
                firstPoint = secondPoint
            else:
                firstPoint = secondPoint
            secIndex += 1
            datumIndex += 1
        secIndex += 2
        datumIndex += 1
        # skip one index since the partition from cylinder to dome is already there from the part generation

    else:
        # Only Dome
        secIndex = 1

    # Partition the dome
    print("Begin Dome Loop")
    firstPoint = pointsOnFace[secIndex - 1][1]
    print(firstPoint)
    for sIndex in range(secIndex, len(keysPointsOnFace)):
        secondPoint = pointsOnFace[sIndex][1]
        print(sIndex)
        print(datumIndex)
        print(firstPoint)
        print(secondPoint)
        pickedFaces = f.findAt((firstPoint, secondPoint))
        d = myPart.datums[datumIndex]
        myPart.PartitionFaceByDatumPlane(datumPlane=d, faces=pickedFaces)
        firstPoint = secondPoint
        datumIndex += 1
    # End of the partition loop

    return pointsOnFace


def rotatePoint(point, rotationAngle):
    rotatedPoint = (
        point[0],
        point[1] * np.cos(np.deg2rad(rotationAngle)),
        point[1] * np.sin(np.deg2rad(rotationAngle)),
    )
    return rotatedPoint


def pointsNearSurfaceOnSections(partionAtPoints):
    pointleft = partionAtPoints[0]
    partionAtPoints = partionAtPoints[1:]
    pointsNearSurface = []
    for pointRight in partionAtPoints:
        pointsNearSurface.append(
            ((pointleft[0] + pointRight[0]) / 2, (pointleft[1] + pointRight[1]) / 2, (pointleft[2] + pointRight[2]) / 2)
        )
        pointleft = pointRight
    return tuple(pointsNearSurface)


"Assign LayUp to Sections Functions------------------------------------------------------------------------------------"


def assignLayUptoSections(
    part,
    pointsOnPation,
    layUpDef,
    projectedAngles,
    matDatabase,
    homMatDatabase,
    processList,
    IDCylDat,
    IDPolarDat,
    tank90=False,
):
    for sec in range(1, layUpDef.shape[1] + 1, 1):
        layersAre1 = [layer + 1 for layer in range(layUpDef.shape[0]) if layUpDef[layer, sec - 1] == 1]
        addLayUptoSection(
            part,
            sec,
            layersAre1,
            pointsOnPation[sec - 1][1],
            projectedAngles[:, sec - 1],
            matDatabase,
            homMatDatabase,
            processList,
            IDCylDat,
            IDPolarDat,
            tank90,
        )


def addLayUptoSection(
    part,
    section,
    laminas,
    pointOnSection,
    projectedAngles,
    matDatabase,
    homMatDatabase,
    processList,
    IDCylDat,
    IDPolarDat,
    tank90=False,
):
    coSysPolar = part.datums[IDPolarDat]
    coSysCylindrical = part.datums[IDCylDat]

    f = part.faces

    face = f.findAt((pointOnSection,))
    region = regionToolset.Region(faces=face)
    compositeLayup = part.CompositeLayup(
        name="LayUpSec-" + str(section),
        description="",
        elementType=SHELL,
        offsetType=BOTTOM_SURFACE,
        symmetric=False,
        thicknessAssignment=FROM_SECTION,
    )

    compositeLayup.Section(
        preIntegrate=OFF,
        integrationRule=SIMPSON,
        thicknessType=UNIFORM,
        poissonDefinition=DEFAULT,
        temperature=GRADIENT,
        useDensity=OFF,
    )
    compositeLayup.ReferenceOrientation(
        orientationType=SYSTEM,
        localCsys=coSysCylindrical,
        fieldName="",
        additionalRotationType=ROTATION_ANGLE,
        angle=90.0,
        additionalRotationField="",
        axis=AXIS_1,
    )
    if tank90:
        laminas = laminas[::-1]

    for lamina in laminas:
        process = processList[lamina - 1]
        materialName = getMaterialName(section, lamina, homMatDatabase)
        if (
            process == "IsoAngleSteering"
            or process == "WindingStyleGeo"
            or process == "CSTable"
            or process == "IsoAngSteerLimitsV1"
        ):
            compositeLayup.CompositePly(
                suppressed=False,
                plyName="Ply-" + str(lamina),
                region=region,
                material=materialName,
                thicknessType=SPECIFY_THICKNESS,
                thickness=homMatDatabase[materialName]["t"],
                orientationType=SPECIFY_ORIENT,
                orientationValue=projectedAngles[lamina - 1],
                additionalRotationField="",
                axis=AXIS_3,
                numIntPoints=3,
            )

        elif process == "PolarPatch":
            compositeLayup.CompositePly(
                suppressed=False,
                plyName="Ply-" + str(lamina),
                region=region,
                material=materialName,
                thicknessType=SPECIFY_THICKNESS,
                thickness=matDatabase[materialName]["t"],
                orientationType=CSYS,
                orientation=coSysPolar,
                additionalRotationType=ROTATION_NONE,
                additionalRotationField="",
                axis=AXIS_1,
                angle=projectedAngles[lamina - 1],
                numIntPoints=3,
            )


def getMaterialName(section, lamina, homMatDatabase):
    materialKey = "Mat_Sec-" + str(section) + "_Lay-" + str(lamina)
    materialValue = homMatDatabase[materialKey]
    if isinstance(materialValue, dict):
        materialName = materialKey

    else:
        materialName = homMatDatabase[materialKey]

    return str(materialName)


"Create Assembly Functions---------------------------------------------------------------------------------------------"


def createAssembly(myModel, myPart):
    myAssembly = myModel.rootAssembly
    myAssembly.DatumCsysByDefault(CARTESIAN)
    myInstance = myAssembly.Instance(name=myPart.name + "-1", part=myPart, dependent=ON)
    myAssembly.DatumCsysByThreePoints(
        coordSysType=CYLINDRICAL,
        name="CSYS_Cylindrical",
        origin=(0.0, 0.0, 0.0),
        point1=(0.0, 1.0, 0.0),
        point2=(0.0, 0.0, 1.0),
    )
    myCSYS = myAssembly.features["CSYS_Cylindrical"]
    myAssembly.regenerate()

    return myInstance, myCSYS


"Create Step Functions-------------------------------------------------------------------------------------------------"


def createStep(myModel, maxNumInc=1000, initialInc=0.1, minInc=1e-10, maxInc=0.25):
    myModel.StaticStep(
        name="StaticGeneralStep",
        previous="Initial",
        maxNumInc=maxNumInc,
        initialInc=initialInc,
        minInc=minInc,
        maxInc=maxInc,
        nlgeom=ON,
    )
    myModel.rootAssembly.regenerate()


"Create Field Output Functions-----------------------------------------------------------------------------------------"


def setGlobalFieldOutput(myModel, FieldOutputName):
    myModel.fieldOutputRequests[FieldOutputName].setValues(
        variables=("CF,E,LE,NT,RF,TEMP,THE,U,"), position=INTEGRATION_POINTS
    )


def createCompositesFieldOutput(myModel, layUpDef, tank360=True):
    if tank360:
        partName = "AFP360Tank"
    else:
        partName = "AFP1/4Tank"

    for section in range(1, layUpDef.shape[1] + 1, 1):
        myModel.FieldOutputRequest(
            name="F-Output-Section-" + str(section),
            createStepName="StaticGeneralStep",
            variables=(
                "S",
                "E",
                "EE",
                "THE",
                "LE",
                "U",
                "RF",
                "CF",
                "NT",
                "TEMP",
            ),
            layupNames=(str(partName) + "-1.LayUpSec-" + str(section),),
            layupLocationMethod=SPECIFIED,
            outputAtPlyTop=True,
            outputAtPlyMid=True,
            outputAtPlyBottom=True,
            rebar=EXCLUDE,
        )


"Create Coupling Functions---------------------------------------------------------------------------------------------"


def createConstraintCoupling(myModel, pointOnEdge, IDRefPoint, IDCylDatum):
    myModel.rootAssembly.ReferencePoint(point=(0.0, 0.0, 0.0))

    regionReferencePoint = regionToolset.Region(referencePoints=(myModel.rootAssembly.referencePoints[IDRefPoint],))

    edges = myModel.rootAssembly.instances["AFP360Tank-1"].edges.findAt((pointOnEdge,))
    regionEdge = regionToolset.Region(edges=edges)

    datumCy = myModel.rootAssembly.instances["AFP360Tank-1"].datums[IDCylDatum]

    myModel.Coupling(
        name="Constraint-Coupling",
        controlPoint=regionReferencePoint,
        surface=regionEdge,
        influenceRadius=WHOLE_SURFACE,
        couplingType=KINEMATIC,
        alpha=0.0,
        localCsys=datumCy,
        u1=OFF,
        u2=ON,
        u3=ON,
        ur1=ON,
        ur2=ON,
        ur3=ON,
    )


"Create BC Functions---------------------------------------------------------------------------------------------------"


def createBC360tank(myModel, IDRefPoint):
    regionReferencePoint = regionToolset.Region(referencePoints=(myModel.rootAssembly.referencePoints[IDRefPoint],))
    myModel.EncastreBC(name="BC-RefPoint", createStepName="Initial", region=regionReferencePoint, localCsys=None)


def createBC90tank(myModel, myInstance, setDict, myCSYS=None):
    myAssembly = myModel.rootAssembly

    for key, value in setDict.items():
        if value:
            region = myInstance.sets[key]
            myModel.DisplacementBC(
                name="BC" + key,
                createStepName="Initial",
                region=region,
                u1=SET if value[0] else UNSET,
                u2=SET if value[1] else UNSET,
                u3=SET if value[2] else UNSET,
                ur1=SET if value[3] else UNSET,
                ur2=SET if value[4] else UNSET,
                ur3=SET if value[5] else UNSET,
                amplitude=UNSET,
                distributionType=UNIFORM,
                fieldName="",
                localCsys=None if myCSYS is None else myAssembly.datums[myCSYS.id],
            )
    myAssembly.regenerate()


"Create Load Functions-------------------------------------------------------------------------------------------------"


def createLoad(myModel, myInstance, nameSurface, nameStep, pressureInnerTank):
    region = myInstance.surfaces[nameSurface]
    myModel.Pressure(
        name="pressureInnerTank",
        createStepName=nameStep,
        region=region,
        distributionType=UNIFORM,
        field="",
        magnitude=pressureInnerTank,
        amplitude=UNSET,
    )
    myModel.rootAssembly.regenerate()


"Create Temperature Fields---------------------------------------------------------------------------------------------"


def createHomogenTemperatureFields(myModel, Tinitial, Tload):
    createHomogenTempertureField(myModel, "Initial", "Set-Thermal", "initialField", Tinitial)
    createHomogenTempertureField(myModel, "StaticGeneralStep", "Set-Thermal", "loadField", Tload)


def createHomogenTempertureField(myModel, stepName, setName, fieldName, T):
    region = myModel.rootAssembly.instances["AFP360Tank-1"].sets[setName]
    myModel.Temperature(
        name=fieldName,
        createStepName=stepName,
        region=region,
        distributionType=UNIFORM,
        crossSectionDistribution=CONSTANT_THROUGH_THICKNESS,
        magnitudes=(T,),
    )


"Create Mesh Functions-------------------------------------------------------------------------------------------------"


def meshWithEdgeSeed360FreeControl(
    myPart, maxElmSizePartSeed, minElSizePartSeed, edgeSeedSize, sectionBorderPoints, edgeSeedUserInput, deviFactor=0.01
):
    partionXYandXZPlane(myPart, 5, 6)
    partSeed(myPart, maxElmSizePartSeed, minElSizePartSeed, deviFactor)
    edgeSeeds360(myPart, edgeSeedSize, sectionBorderPoints, edgeSeedUserInput)
    myPart.generateMesh()


def meshWithGradientEdgeSeed360SweepControl(myPart, maxElmSize, minElSize, sectionBorderPoints, deviFactor=0.01):
    partionXYandXZPlane(myPart, 5, 6)

    partSeed(myPart, maxElmSize, minElSize, deviFactor)
    edgeSeeds360Gradient(myPart, maxElmSize, minElSize, sectionBorderPoints)
    sweepControl(myPart)
    myPart.generateMesh()


def meshWithEdgeSeedControl(myPart, maxElmSize, minElSize, sectionBorderPoints, deviFactor=0.01):
    partSeed(myPart, maxElmSize, minElSize, deviFactor)
    edgeSeedsQuarterTank(myPart, maxElmSize, minElSize, sectionBorderPoints)
    sweepControl(myPart)
    myPart.generateMesh()


def partionXYandXZPlane(myPart, IDXYPlane, IDXZPlane):
    pickedFaces = myPart.faces[:]
    d = myPart.datums[IDXYPlane]
    myPart.PartitionFaceByDatumPlane(datumPlane=d, faces=pickedFaces)

    pickedFaces = myPart.faces[:]
    d = myPart.datums[IDXZPlane]
    myPart.PartitionFaceByDatumPlane(datumPlane=d, faces=pickedFaces)


def partSeed(myPart, maxElmSize, minElSize, deviFactor):
    myPart.seedPart(size=maxElmSize, deviationFactor=deviFactor, minSizeValue=minElSize)


def edgeSeedsQuarterTank(myPart, maxElmSize, minElSize, sectionBorderPoints):
    gradientEdgeSeed = 2 * (maxElmSize - minElSize) / (sectionBorderPoints[-1][0] - sectionBorderPoints[0][0])
    # no deep reasoning behind multiplying gradientedgeSeed with 2
    sectionBorderPoints = sectionBorderPoints[::-1]

    rightBorderPoint = sectionBorderPoints[0]
    minElmSizeSec = minElSize
    globalMaxElmSize = maxElmSize
    for leftBorderPoint in sectionBorderPoints[1:]:
        maxElmSizeSec = (rightBorderPoint[0] - leftBorderPoint[0]) * gradientEdgeSeed + minElmSizeSec
        if globalMaxElmSize < maxElmSizeSec:
            break

        edgeY = getEdge(
            myPart.edges,
            (0.5 * (rightBorderPoint[0] + leftBorderPoint[0]), 0.5 * (rightBorderPoint[1] + leftBorderPoint[1]), 0),
            0,
        )
        edgeZ = getEdge(
            myPart.edges,
            (0.5 * (rightBorderPoint[0] + leftBorderPoint[0]), 0.5 * (rightBorderPoint[1] + leftBorderPoint[1]), 0),
            90,
        )

        myPart.seedEdgeByBias(
            biasMethod=SINGLE,
            end1Edges=edgeZ,
            end2Edges=edgeY,
            minSize=minElmSizeSec,
            maxSize=maxElmSizeSec,
            constraint=FINER,
        )
        minElmSizeSec = maxElmSizeSec
        rightBorderPoint = leftBorderPoint


def edgeSeeds360(myPart, globalEdgeSeedSize, sectionBorderPoints, edgeSeedUserInput):
    sectionBorderPoints = sectionBorderPoints[::-1]
    edgeSeedUserInput = edgeSeedUserInput[::-1]
    edgeSeedIsNan = np.isnan(edgeSeedUserInput)

    rightBorderPoint = sectionBorderPoints[0]

    for i, leftBorderPoint in enumerate(sectionBorderPoints[1:]):
        averageBorderPointX = 0.5 * (rightBorderPoint[0] + leftBorderPoint[0])
        averageBorderPointY = 0.5 * (rightBorderPoint[1] + leftBorderPoint[1])
        averageBorderPointZ = 0.0

        pointEdgeYTop = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 0
        )
        pointEdgeZLeft = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 90
        )
        pointEdgeYBottom = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 180
        )
        pointEdgeZRight = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 270
        )

        if edgeSeedIsNan[i]:
            edgeSize = globalEdgeSeedSize
        else:
            edgeSize = edgeSeedUserInput[i]
        myPart.seedEdgeBySize(
            size=edgeSize,
            edges=myPart.edges.findAt((pointEdgeZRight,), (pointEdgeYTop,), (pointEdgeZLeft,), (pointEdgeYBottom,)),
            deviationFactor=0.1,
            constraint=FINER,
        )
        # print("Index {} leftborderpoint {} , rightboderpoint {}".format(i, leftBorderPoint, rightBorderPoint))
        # print("Edge Seed {}".format(edgeSize))
        rightBorderPoint = leftBorderPoint


def edgeSeeds360Gradient(myPart, maxElmSize, minElSize, sectionBorderPoints):
    gradientEdgeSeed = 2 * (maxElmSize - minElSize) / (sectionBorderPoints[-1][0] - sectionBorderPoints[0][0])
    # no deep reasoning behind multiplying gradientedgeSeed with 2
    sectionBorderPoints = sectionBorderPoints[::-1]

    rightBorderPoint = sectionBorderPoints[0]
    minElmSizeSec = minElSize
    globalMaxElmSize = maxElmSize
    for leftBorderPoint in sectionBorderPoints[1:]:
        maxElmSizeSec = (rightBorderPoint[0] - leftBorderPoint[0]) * gradientEdgeSeed + minElmSizeSec
        if globalMaxElmSize < maxElmSizeSec:
            break

        averageBorderPointX = 0.5 * (rightBorderPoint[0] + leftBorderPoint[0])
        averageBorderPointY = 0.5 * (rightBorderPoint[1] + leftBorderPoint[1])
        averageBorderPointZ = 0.0

        pointEdgeYTop = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 0
        )
        pointEdgeZLeft = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 90
        )
        pointEdgeYBottom = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 180
        )
        pointEdgeZRight = getClosesdPointOnEdge(
            myPart.edges, (averageBorderPointX, averageBorderPointY, averageBorderPointZ), 270
        )

        myPart.seedEdgeByBias(
            biasMethod=SINGLE,
            end1Edges=myPart.edges.findAt((pointEdgeZRight,)),
            end2Edges=myPart.edges.findAt((pointEdgeYTop,), (pointEdgeZLeft,), (pointEdgeYBottom,)),
            minSize=minElmSizeSec,
            maxSize=maxElmSizeSec,
            constraint=FINER,
        )
        minElmSizeSec = maxElmSizeSec
        rightBorderPoint = leftBorderPoint


def sweepControl(myPart):
    allRegions = myPart.faces[:]
    myPart.setMeshControls(regions=allRegions, technique=SWEEP)


"Add Larc in KeywordBlock Object to each FieldOutput"


def insertLarcToFieldOutput(myModel):
    positions = GetKeywordPositions(myModel, "S, TEMP, THE")
    i = 0
    for position in positions:
        myModel.keywordBlock.insert(position + 1 + i, ", LARCMCCRT, LARCFKCRT, LARCFSCRT, LARCFTCRT")
        i = i + 1


def GetKeywordPositions(myModel, blockPrefix):
    # Function adapted from Felipe Franzoni
    myModel.keywordBlock.synchVersions(storeNodesAndElements=True)
    sieBlocks = myModel.keywordBlock.sieBlocks
    positionList = []

    if blockPrefix == " ":
        position = len(sieBlocks) - 2
        return positionList.append(position)
    else:
        for i in range(len(sieBlocks)):
            sieBlock = sieBlocks[i]
            if sieBlock.find(blockPrefix) > -1:
                position = i - 1
                positionList.append(position)
    return positionList


"Create Job Functions--------------------------------------------------------------------------------------------------"


def createJob(myModel, scratchDir):
    myModel.rootAssembly.regenerate()

    mdb.Job(
        name=myModel.name,
        model=myModel.name,
        description="",
        type=ANALYSIS,
        atTime=None,
        waitMinutes=0,
        waitHours=0,
        queue=None,
        memory=90,
        memoryUnits=PERCENTAGE,
        getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE,
        nodalOutputPrecision=SINGLE,
        echoPrint=OFF,
        modelPrint=OFF,
        contactPrint=OFF,
        historyPrint=OFF,
        userSubroutine="",
        scratch=scratchDir,
        resultsFormat=ODB,
        multiprocessingMode=DEFAULT,
        numCpus=1,
        numGPUs=0,
    )
    mdb.jobs[myModel.name].writeInput(consistencyChecking=OFF)
