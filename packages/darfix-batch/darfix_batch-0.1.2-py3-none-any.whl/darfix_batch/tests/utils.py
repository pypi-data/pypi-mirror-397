import numpy
from silx.io.dictdump import dicttoh5


def create_dataset(filename: str):
    h5dict = {
        "1.1": _create_scan(),
        "1.2": {},
        "2.1": _create_scan(),
        "2.2": {},
    }
    return dicttoh5(h5dict, filename)


def _create_scan() -> dict:
    return {
        "measurement": {"detector": numpy.ones(shape=(10, 10, 10), dtype=numpy.uint16)},
        "instrument": {"positioners": {"motor_1": numpy.arange(10)}},
    }
