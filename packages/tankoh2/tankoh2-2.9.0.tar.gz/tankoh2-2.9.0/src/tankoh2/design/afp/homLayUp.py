from tankoh2 import log

"""main"""


def homLayUp(layUp):
    log.infoHeadline("**HomLayUp")
    # homogenize the layup and save it at the dedicated attributes of the obj
    layUp.projectAngles(
        layUp.simulationParameters["FlagTowCuttingStartAtDomeStart"],
        layUp.simulationParameters["FlagGapFunctionOn"],
    )
    layUp.homMatProp = calculateMatrixPropertiesAll(layUp)
    return layUp


"""Functions to calculate the homogenized fiber-, matrix- and gap volume share
 of a specific layer in a specific section."""


def calculateMatrixPropertiesAll(LayUpObj):
    homMaterialDatabase = {}
    for section in range(1, LayUpObj.sections + 1, 1):
        for Layer in range(1, LayUpObj.layUpDefinition.shape[0] + 1, 1):
            if LayUpObj.layUpDesign[Layer - 1, section - 1] == 1:
                Process = LayUpObj.layUpDefinition["Process"][Layer - 1]
                if (
                    Process == "WindingStyleGeo"
                    or Process == "IsoAngleSteering"
                    or Process == "IsoAngSteerLimitsV1"
                    or Process == "CSTable"
                ):  # add your new Process here
                    # Calculate new matrix properties
                    projectedMaterial = calculateMatrixPropertiesForLayerInSection(LayUpObj, section, Layer)
                    name = "Mat_Sec-" + str(section) + "_Lay-" + str(Layer)
                    homMaterialDatabase[name] = projectedMaterial
                elif Process == "PolarPatch":  # or add your new Process here
                    # Do not calculate new Matrix properties and take the base material
                    name = "Mat_Sec-" + str(section) + "_Lay-" + str(Layer)
                    homMaterialDatabase[name] = LayUpObj.layUpDefinition["Material"][Layer - 1]
                else:
                    raise Exception(
                        "Specify in calculateMatrixPropertiesAll(),\n"
                        " whether new Matrix properties shall be calculated (if) or not (elif) "
                    )

    return homMaterialDatabase


def calculateMatrixPropertiesForLayerInSection(LayUpObj, Section, Layer):
    materialBaseline = LayUpObj.getLayerMaterial(Layer)
    materialHomogenized = {}

    phiFibre, phiRes, phiGap = materialVolumeShareProperties(LayUpObj, Section, Layer)

    E1 = E1MixingRule(materialBaseline["Efiber"], phiFibre, materialBaseline["Eres"], phiRes)
    E2 = E2MixingRule(materialBaseline["Efiber"], phiFibre, materialBaseline["Eres"], phiRes)
    Nu12 = Nu12MixingRule(materialBaseline["Nu12fiber"], phiFibre, materialBaseline["Nu12res"], phiRes)
    Nu23 = Nu23MixingRule(materialBaseline["Nu23fiber"], phiFibre, materialBaseline["Nu12res"], phiRes)
    G12 = G12MixingRule(materialBaseline["G12fiber"], phiFibre, materialBaseline["G12res"], phiRes)
    G13 = G12
    G23 = G23MixingRule(E2, Nu23)
    Roh = RohMixingRule(materialBaseline["Rohfiber"], phiFibre, materialBaseline["Rohres"], phiRes + phiGap)
    Xt = XtMixingRule(materialBaseline["Xt"], materialBaseline["phiFiber"], phiFibre)
    Xc = XcMixingRule(materialBaseline["Xc"], materialBaseline["phiFiber"], phiFibre)
    Yt = XtMixingRule(materialBaseline["Yt"], materialBaseline["phiFiber"], phiFibre)
    Yc = XcMixingRule(materialBaseline["Yc"], materialBaseline["phiFiber"], phiFibre)
    Sl = SlMixingRule(materialBaseline["Sl"], materialBaseline["phiFiber"], phiFibre)
    alpha0 = materialBaseline["alpha0"]
    psi0 = materialBaseline["psi0"]
    St = StMixingRule(materialBaseline["St"], materialBaseline["phiFiber"], phiFibre)

    materialHomogenized["E1"] = E1
    materialHomogenized["E2"] = E2
    materialHomogenized["Nu12"] = Nu12
    materialHomogenized["Nu23"] = Nu23
    materialHomogenized["G12"] = G12
    materialHomogenized["G13"] = G13
    materialHomogenized["G23"] = G23
    materialHomogenized["t"] = materialBaseline["t"]
    materialHomogenized["Roh"] = Roh
    materialHomogenized["Xt"] = Xt
    materialHomogenized["Xc"] = Xc
    materialHomogenized["Yt"] = Yt
    materialHomogenized["Yc"] = Yc
    materialHomogenized["Sl"] = Sl
    materialHomogenized["alpha0"] = alpha0
    materialHomogenized["psi0"] = psi0
    materialHomogenized["St"] = St
    # Todo combine the two blocks !

    # Coefficients of Thermal Expansion
    # currently no recalculation/mixing of thermal coefficients
    materialHomogenized["CTE1"] = materialBaseline["CTE1"]
    materialHomogenized["CTE2"] = materialBaseline["CTE2"]
    materialHomogenized["CTE3"] = materialBaseline["CTE3"]

    return materialHomogenized


def materialVolumeShareProperties(LayUpObj, section, layer):
    gapVolShare = LayUpObj.projectedSecPhiGap[layer - 1, section - 1]
    fibreVolShare = fibreVolumeShare(LayUpObj.getLayerMaterialProperty(layer, "phiFiber"), gapVolShare)
    resignVolumeShare = resignVolumeShareF(LayUpObj.getLayerMaterialProperty(layer, "phiFiber"), gapVolShare)

    return fibreVolShare, resignVolumeShare, gapVolShare


def fibreVolumeShare(fibreVolumeShareMaterial, gapVolumeShare):
    return fibreVolumeShareMaterial * (1 - gapVolumeShare)


def resignVolumeShareF(fibreVolumeShareMaterial, gapVolumeShare):
    return (1 - fibreVolumeShareMaterial) * (1 - gapVolumeShare)


def E1MixingRule(Efibre, Vfibre, Ematrix, Vmatrix):
    return Efibre * Vfibre + Ematrix * Vmatrix


def E2MixingRule(Efibre, Vfibre, Ematrix, Vmatrix):
    return Efibre * Ematrix / (Vmatrix * Efibre + Vfibre * Ematrix)


def Nu12MixingRule(Nu12fibre, Vfibre, Nu12matrix, Vmatrix):
    return Nu12fibre * Vfibre + Nu12matrix * Vmatrix


def Nu23MixingRule(Nu23fibre, Vfibre, Nu23matrix, Vmatrix):
    return Nu23fibre * Vfibre + Nu23matrix * Vmatrix


def G12MixingRule(G12fibre, Vfibre, G12matrix, Vmatrix):
    return G12fibre * G12matrix / (Vmatrix * G12fibre + Vfibre * G12matrix)


def G23MixingRule(E2, Nu23):
    return E2 / (2 * (1 + Nu23))


def RohMixingRule(Rohfibre, Vfibre, Rohres, Vmatrix):
    # Todo review this rule
    return Rohfibre * Vfibre + Rohres * Vmatrix


def XtMixingRule(Xt, VfibreBaseline, VfibreHomogenized):
    # Todo review this rule
    return Xt * (1 - abs((VfibreBaseline - VfibreHomogenized) / VfibreBaseline))


def XcMixingRule(Xc, VfibreBaseline, VfibreHomogenized):
    # Todo review this rule
    return Xc * (1 - abs((VfibreBaseline - VfibreHomogenized) / VfibreBaseline))


def YtMixingRule(Yt, VfibreBaseline, VfibreHomogenized):
    # Todo review this rule
    return Yt * (1 - abs((VfibreBaseline - VfibreHomogenized) / VfibreBaseline))


def YcMixingRule(Yc, VfibreBaseline, VfibreHomogenized):
    # Todo review this rule
    return Yc * (1 - abs((VfibreBaseline - VfibreHomogenized) / VfibreBaseline))


def SlMixingRule(Sl, VfibreBaseline, VfibreHomogenized):
    # Todo review this rule
    return Sl * (1 - abs((VfibreBaseline - VfibreHomogenized) / VfibreBaseline))


def StMixingRule(St, VfibreBaseline, VfibreHomogenized):
    # Todo review this rule
    return St * (1 - abs((VfibreBaseline - VfibreHomogenized) / VfibreBaseline))
