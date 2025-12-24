import pandas as pd

from tankoh2.geometry.dome import DomeTorispherical

dt = DomeTorispherical(850, 50)

contour = dt.getContour(200)
print(contour)

pdata = pd.DataFrame(contour)

pdata.to_excel("OutputDomeToris.xlsx")
