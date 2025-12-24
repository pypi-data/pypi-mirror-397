# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


def getReducedDomePoints(contourFilename, spacing=1, contourOutFilename=None):
    """

    :param contourFilename: path to file. The file has 2 rows with x and r coordinates
    :param spacing:
    :param contourOutFilename:
    :return: [x,r]
    """
    # load contour from file
    contourPoints = np.abs(np.loadtxt(contourFilename))
    contourPoints[:, 0] -= contourPoints[0, 0]
    # reduce points
    redContourPoints = contourPoints[::spacing, :]
    if not np.allclose(redContourPoints[-1, :], contourPoints[-1, :]):
        redContourPoints = np.append(redContourPoints, [contourPoints[-1, :]], axis=0)
    if contourOutFilename:
        np.savetxt(contourOutFilename, redContourPoints, delimiter=",")
    Xvec, rVec = redContourPoints[:, 0], redContourPoints[:, 1]

    return np.array([Xvec, rVec])


def contourLength(x, r):
    """Returns the contour length of a dome"""
    contourCoords = np.array([x, r]).T
    contourDiffs = contourCoords[1:, :] - contourCoords[:-1]
    contourLength = np.sum(np.linalg.norm(contourDiffs, axis=1))
    return contourLength


def getRadiusByShiftOnContour(radii, lengths, startRadius, shift):
    """Calculates a shift along the mandrel surface in the dome section

    :param radii: vector of radii
    :param lengths: vector of lengths with same length as radii
    :param startRadius: radius on mandrel where the shift should be applied
    :param shift: (Scalar or Vector) Shift along the surface. Positive values shift in fitting direction
    :return: radius
    """
    # x-coordinate, radius, length on mandrel
    coords = pd.DataFrame(np.array([radii, lengths]).T, columns=["r", "l"])

    # cut section of above 0.9*maxRadius
    maxR = coords["r"].max()
    coords = coords[coords["r"] < 0.9 * maxR]

    # invert index order
    coordsRev = coords.iloc[::-1]

    # get initial length and perform shift
    lengthInterp = interp1d(coordsRev["r"], coordsRev["l"], fill_value="extrapolate", assume_sorted=True)
    startLength = lengthInterp(startRadius)
    targetLength = startLength + shift

    # get target radius
    radiusInterpolation = interp1d(coords["l"], coords["r"], fill_value="extrapolate", assume_sorted=True)
    targetRadius = radiusInterpolation(targetLength)
    return targetRadius


def getCoordsShiftFromLength(x, r, l, startLength, shift):
    """Calculates a shift along the mandrel surface in the dome section

    :param x: vector with x-coords
    :param r: vector with radius-coords
    :param l: vector with contour length-coords
    :param startLength: length on mandrel where the shift should be applied
    :param shift: (Scalar or Vector) Shift along the surface. Positive values shift in fitting direction
    :return: 4-tuple with scalar or vector entires depending on parameter "shift"
        x-coordinate, radius, length, nearestElementIndices

    """
    targetLength = startLength + shift

    targetRadius = np.interp(targetLength, l, r)
    targetX = np.interp(targetLength, l, x)
    elementLengths = (l[:-1] + l[1:]) / 2
    elementLengths = np.array([elementLengths] * len(targetLength))
    indicies = np.argmin(np.abs(elementLengths.T - targetLength), axis=0)
    return targetX, targetRadius, targetLength, indicies


def getXR4Testing():
    """returns axial coordinate and radius of test geometry"""
    radius = np.array(
        [
            850,
            850,
            849.9908489,
            849.9633938,
            849.9176288,
            849.8535443,
            849.7711269,
            849.6703593,
            849.5512202,
            849.4136845,
            849.2577231,
            849.083303,
            848.8903871,
            848.6789343,
            848.4488995,
            848.2002332,
            847.9328821,
            847.6467883,
            847.3418898,
            847.01812,
            846.6754082,
            846.3136788,
            845.9328518,
            845.5328423,
            845.1135608,
            844.6749128,
            844.2167987,
            843.7391138,
            843.2417482,
            842.7245865,
            842.1875077,
            841.6303852,
            841.0530866,
            840.4554733,
            839.8374006,
            839.1987173,
            838.5392658,
            837.8588813,
            837.1573923,
            836.43462,
            835.6903777,
            834.9244712,
            834.1366982,
            833.3268478,
            832.4947003,
            831.6400273,
            830.7625906,
            829.8621421,
            828.9384238,
            827.9911666,
            827.0200905,
            826.0249038,
            825.0053024,
            823.9609695,
            822.8915751,
            821.796775,
            820.6762101,
            819.5295062,
            818.3562724,
            817.156101,
            815.9285661,
            814.6732227,
            813.3896057,
            812.0772289,
            810.7355834,
            809.3641365,
            807.9623303,
            806.52958,
            805.0652724,
            803.5687638,
            802.039378,
            800.4764045,
            798.8790958,
            797.2466648,
            795.578282,
            793.8730727,
            792.1301129,
            790.3484262,
            788.5269793,
            786.6646775,
            784.7603595,
            782.8127921,
            780.8206632,
            778.7825755,
            776.6970383,
            774.5624586,
            772.3771312,
            770.1392274,
            767.8467825,
            765.4976807,
            763.0896392,
            760.6201883,
            758.0866503,
            755.4861133,
            752.8154022,
            750.0710435,
            747.2492249,
            744.3457471,
            741.3559658,
            738.2747233,
            735.0962642,
            731.8141338,
            728.4210526,
            724.9865272,
            721.5291204,
            718.0485016,
            714.5443316,
            711.0162623,
            707.4639361,
            703.8869857,
            700.2850337,
            696.6576925,
            693.0045633,
            689.3252361,
            685.6192892,
            681.8862885,
            678.1257872,
            674.3373254,
            670.5204289,
            666.6746095,
            662.7993637,
            658.8941723,
            654.9584995,
            650.9917927,
            646.9934809,
            642.9629746,
            638.8996645,
            634.8029206,
            630.6720914,
            626.5065027,
            622.3054564,
            618.0682296,
            613.7940729,
            609.4822095,
            605.1318332,
            600.7421073,
            596.312163,
            591.841097,
            587.3279702,
            582.7718055,
            578.1715853,
            573.5262497,
            568.8346933,
            564.0957628,
            559.3082541,
            554.4709089,
            549.5824111,
            544.6413835,
            539.6463831,
            534.595897,
            529.4883376,
            524.3220368,
            519.0952409,
            513.8061036,
            508.4526795,
            503.032916,
            497.5446453,
            491.9855747,
            486.3532765,
            480.6451763,
            474.8585407,
            468.9904626,
            463.0378456,
            456.9973863,
            450.8655541,
            444.6385688,
            438.3123749,
            431.8826129,
            425.3445859,
            418.6932223,
            411.9230319,
            405.028056,
            398.0018094,
            390.8372124,
            383.5265115,
            376.061186,
            368.4318369,
            360.6280541,
            352.6382573,
            344.4495025,
            336.0472455,
            327.4150498,
            318.534222,
            309.3833521,
            299.9377246,
            290.168556,
            280.0419885,
            269.5177396,
            258.5472504,
            247.0710862,
            235.0151798,
            222.2852222,
            208.7579398,
            194.2668448,
            178.5774587,
            161.3405798,
            141.9937631,
            119.5167227,
            91.63425899,
            50,
        ]
    )
    x = np.array(
        [
            0,
            800,
            802.1889317,
            804.3778634,
            806.5667951,
            808.7557269,
            810.9446586,
            813.1335903,
            815.322522,
            817.5114537,
            819.7003854,
            821.8893172,
            824.0782489,
            826.2671806,
            828.4561123,
            830.645044,
            832.8339757,
            835.0229075,
            837.2118392,
            839.4007709,
            841.5897026,
            843.7786343,
            845.967566,
            848.1564977,
            850.3454295,
            852.5343612,
            854.7232929,
            856.9122246,
            859.1011563,
            861.290088,
            863.4790198,
            865.6679515,
            867.8568832,
            870.0458149,
            872.2347466,
            874.4236783,
            876.6126101,
            878.8015418,
            880.9904735,
            883.1794052,
            885.3683369,
            887.5572686,
            889.7462003,
            891.9351321,
            894.1240638,
            896.3129955,
            898.5019272,
            900.6908589,
            902.8797906,
            905.0687224,
            907.2576541,
            909.4465858,
            911.6355175,
            913.8244492,
            916.0133809,
            918.2023127,
            920.3912444,
            922.5801761,
            924.7691078,
            926.9580395,
            929.1469712,
            931.3359029,
            933.5248347,
            935.7137664,
            937.9026981,
            940.0916298,
            942.2805615,
            944.4694932,
            946.658425,
            948.8473567,
            951.0362884,
            953.2252201,
            955.4141518,
            957.6030835,
            959.7920153,
            961.980947,
            964.1698787,
            966.3588104,
            968.5477421,
            970.7366738,
            972.9256056,
            975.1145373,
            977.303469,
            979.4924007,
            981.6813324,
            983.8702641,
            986.0591958,
            988.2481276,
            990.4370593,
            992.625991,
            994.8149227,
            997.0038544,
            999.1927861,
            1001.381718,
            1003.57065,
            1005.759581,
            1007.948513,
            1010.137445,
            1012.326376,
            1014.515308,
            1016.70424,
            1018.893172,
            1021.082103,
            1023.253259,
            1025.424415,
            1027.595571,
            1029.766727,
            1031.937882,
            1034.109038,
            1036.280194,
            1038.45135,
            1040.622506,
            1042.793661,
            1044.964817,
            1047.135973,
            1049.307129,
            1051.478285,
            1053.64944,
            1055.820596,
            1057.991752,
            1060.162908,
            1062.334064,
            1064.505219,
            1066.676375,
            1068.847531,
            1071.018687,
            1073.189843,
            1075.360998,
            1077.532154,
            1079.70331,
            1081.874466,
            1084.045622,
            1086.216777,
            1088.387933,
            1090.559089,
            1092.730245,
            1094.901401,
            1097.072556,
            1099.243712,
            1101.414868,
            1103.586024,
            1105.75718,
            1107.928335,
            1110.099491,
            1112.270647,
            1114.441803,
            1116.612959,
            1118.784114,
            1120.95527,
            1123.126426,
            1125.297582,
            1127.468738,
            1129.639893,
            1131.811049,
            1133.982205,
            1136.153361,
            1138.324517,
            1140.495672,
            1142.666828,
            1144.837984,
            1147.00914,
            1149.180296,
            1151.351451,
            1153.522607,
            1155.693763,
            1157.864919,
            1160.036075,
            1162.20723,
            1164.378386,
            1166.549542,
            1168.720698,
            1170.891854,
            1173.063009,
            1175.234165,
            1177.405321,
            1179.576477,
            1181.747633,
            1183.918789,
            1186.089944,
            1188.2611,
            1190.432256,
            1192.603412,
            1194.774568,
            1196.945723,
            1199.116879,
            1201.288035,
            1203.459191,
            1205.630347,
            1207.801502,
            1209.972658,
            1212.143814,
            1214.31497,
            1216.486126,
            1218.657281,
            1220.828437,
            1222.999593,
            1225.170749,
            1227.341905,
            1229.51306,
            1231.684216,
        ]
    )
    return x, radius
