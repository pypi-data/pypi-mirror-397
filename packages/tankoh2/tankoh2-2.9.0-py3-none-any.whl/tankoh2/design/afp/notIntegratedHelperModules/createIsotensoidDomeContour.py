import pandas as pd

from tankoh2.geometry.dome import DomeIsotensoid

dt = DomeIsotensoid(197.5, 0.0)

contour = dt.getContour(200)
print(contour)

pdata = pd.DataFrame(contour)

pdata.to_excel("OutputIsotensoid.xlsx")
