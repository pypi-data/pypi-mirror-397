# --- Boundary conditions
bc_set_dict = dict(
    symmX=[True, False, False, False, True, True],
    symmY=[False, True, False, True, False, True],
    symmZ=[False, False, True, True, True, False],
)


# -- Reference Temperature
thermalLoadOn = False
refTemperatureMaterial = 293  # has currently no effect
initialStepTemperature = 293
loadStepTemperature = 20
# --- Step definition
max_num_inc = 1000
initial_inc = 0.1
min_inc = 1e-10
max_inc = 0.25
