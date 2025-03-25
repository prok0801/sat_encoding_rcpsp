from sat.data.project  import Project
from  sat.algorithm.rcpsp import RcpspAlogithm

p = Project("assets/input/test.json")

rcpsp = RcpspAlogithm(p)
rcpsp.calculate()

