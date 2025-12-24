from scipy.optimize import fsolve


# Define the functions representing the two equations
def eqE1(Es, E1, phiFibre):
    return phiFibre * Es[0] + (1 - phiFibre) * Es[1] - E1


def eqE2(Es, E2, phiFibre):
    return (Es[0] * Es[1] / (Es[0] * (1 - phiFibre) + Es[1] * phiFibre)) - E2


def Fun(Es, E1, E2, phiFibre):
    return (eqE1(Es, E1, phiFibre), eqE2(Es, E2, phiFibre))


# Values of E1, E2, phiFibre
E1 = 127015
E2 = 9053
phiFiber = 0.544

# Provide initial guesses for Efibre and Eres
Efibre = 100000
Eres = 1000

# Solve the system using fsolve()
root = fsolve(Fun, [Efibre, Eres], args=(E1, E2, phiFiber))

print(f"Efibre = {root[0]}, Eres = {root[1]}")
