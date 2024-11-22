from typing import NewType, TypeAlias
from xml.etree.ElementTree import Element

import pandas as pd


Frame: TypeAlias = pd.DataFrame
Series: TypeAlias = pd.Series

AnalysisName = NewType('AnalysisName', str)
ProbeName = NewType('ProbeName', str)
ProbeGUID = NewType('ProbeGUID', str)
XML = NewType('XML', Element)
XMLPath = NewType('XMLPath', str)
