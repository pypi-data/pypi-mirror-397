from mrcrowbar import models as mrc

from mrcrowbar import utils

class PPDataEntry(mrc.Block):
    offset = mrc.UInt32_LE()
    path = mrc.CStringN(length=0x18)

class PPData(mrc.Block):
    count = mrc.UInt32_LE()
    entries = mrc.BlockField(PPDataEntry, count=mrc.Ref('count'))
    data_raw = mrc.Bytes()
