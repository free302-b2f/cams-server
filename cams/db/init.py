"""DBMS 초기화 등 """

if __name__ == "__main__":
    import sys, os.path as path

    dir = path.join(path.dirname(__file__), "..")
    sys.path.append(dir)

from apps.imports import *

_set = getConfigSection("Postgres")
_pgc = pg.connect(
    f'postgres://{_set["User"]}:{_set["Pw"]}@{_set["Ip"]}:{_set["Port"]}/{_set["Db"]}'
)



if __name__ == "__main__":
    pass