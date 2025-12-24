import matplotlib.pyplot as plt
import numpy as np


def psiGapFun(r, alpha, b, nTows):
    """
    A self-developed method for calculating
    the gap volume content (psiGap).

    @param r: radii [mm] (numpy array)
    @param alpha: local ply angle [Degree] (numpy array)
    @param b: width of the band [mm]
    @param nTows: number of tows in one band []
    @return: gap volume content [/] (numpy array)
    """
    U = r * 2 * np.pi
    B = b / np.cos(np.deg2rad(alpha))
    Bn = B / nTows

    Xs = B[0] / U[0]
    psiGap = np.zeros(U.shape)
    funDefined = np.empty(U.shape, dtype=bool)
    funDefined[:] = False

    # main iteration over the contour
    for i, u in enumerate(U):
        (ns, rest) = divmod(u * Xs + 0.000001, Bn[i])  # 0.000001 only for numerical reasons to not cut a tow in the
        # cylindrical region

        psiGap[i] = 1 - (ns * Bn[i] / (u * Xs))
        if psiGap[i] > 0.5:
            funDefined[: i - 1] = True
            break

    psiGap[np.invert(funDefined)] = 0.0

    return psiGap, funDefined


if __name__ == "__main__":
    from tankoh2.design.afp.service import radius, x

    alphaArray = np.empty(radius.shape)
    alphaArray[:] = 40

    psiGap, gapFunDefined = psiGapFun(radius, alphaArray, 38.1, 6)

    # Plotting
    fig, ax1 = plt.subplots()

    # Plot the first series with its own y-axis on the left
    ax1.plot(x, psiGap * 100, "b", label="psiGap")
    ax1.set_ylabel("psiGap[%]")
    ax1.ticklabel_format(axis="y", useMathText=True)
    ax1.set_xlabel("x [mm]")

    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()

    # Plot the second series with its own y-axis on the right
    ax2.plot(x, radius, "k", label="Radius Tank")
    ax2.set_ylabel("r [mm]")
    ax2.ticklabel_format(axis="y", useMathText=True)

    # Adjust layout to make room for both y-axes
    fig.tight_layout()

    # Show the plot
    plt.show()
