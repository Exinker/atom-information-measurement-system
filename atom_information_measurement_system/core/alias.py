
from typing import NewType, TypeAlias
from xml.etree.ElementTree import Element

import pandas as pd


Frame: TypeAlias = pd.DataFrame
Series: TypeAlias = pd.Series

AnalysisName = NewType('AnalysisName', str)
XMLPath = NewType('XMLPath', str)
ProbeName = NewType('ProbeName', str)
XML = NewType('XML', Element)

