from __future__ import annotations

from mrcrowbar import models as mrc

class WOPL3Instrument(mrc.Block):
    name = mrc.Bytes(length=32, default=b"\x00"*32)
    midi_key_offset_voice1 = mrc.Int16_BE()
    midi_key_offset_voice2 = mrc.Int16_BE()
    midi_veloc_offset = mrc.Int8()
    voice2_detune = mrc.Int8()
    percussion_key = mrc.UInt8()
    flags = mrc.UInt8()
    reg_c0h_voice1 = mrc.UInt8()
    reg_c0h_voice2 = mrc.UInt8()
    reg_20h_op1 = mrc.UInt8()
    reg_40h_op1 = mrc.UInt8()
    reg_60h_op1 = mrc.UInt8()
    reg_80h_op1 = mrc.UInt8()
    reg_e0h_op1 = mrc.UInt8()
    reg_20h_op2 = mrc.UInt8()
    reg_40h_op2 = mrc.UInt8()
    reg_60h_op2 = mrc.UInt8()
    reg_80h_op2 = mrc.UInt8()
    reg_e0h_op2 = mrc.UInt8()
    reg_20h_op3 = mrc.UInt8()
    reg_40h_op3 = mrc.UInt8()
    reg_60h_op3 = mrc.UInt8()
    reg_80h_op3 = mrc.UInt8()
    reg_e0h_op3 = mrc.UInt8()
    reg_20h_op4 = mrc.UInt8()
    reg_40h_op4 = mrc.UInt8()
    reg_60h_op4 = mrc.UInt8()
    reg_80h_op4 = mrc.UInt8()
    reg_e0h_op4 = mrc.UInt8()
    midi_keyon_delay = mrc.UInt16_BE()
    midi_keyoff_delay = mrc.UInt16_BE()

class WOPL3MelodicBank(mrc.Block):
    instruments = mrc.BlockField(WOPL3Instrument, count=128)

class WOPL3PercussionBank(mrc.Block):
    instruments = mrc.BlockField(WOPL3Instrument, count=128)

class WOPL3Meta(mrc.Block):
    name = mrc.Bytes(length=32, default=b"\x00"*32)
    lsb_index = mrc.UInt8()
    msb_index = mrc.UInt8()

class WOPL3Bank(mrc.Block):
    magic = mrc.Const(mrc.Bytes(length=11, default=b"WOPL3-BANK\x00"), b"WOPL3-BANK\x00")
    version = mrc.Const(mrc.UInt16_LE(default=3), 3)
    melodic_bank_count = mrc.UInt16_BE()
    percussion_bank_count = mrc.UInt16_BE()
    global_flags = mrc.UInt8()
    volume_model = mrc.UInt8()
    melodic_bank_meta = mrc.BlockField(WOPL3Meta, count=mrc.Ref('melodic_bank_count'))
    percussion_bank_meta = mrc.BlockField(WOPL3Meta, count=mrc.Ref('percussion_bank_count'))
    melodic_banks = mrc.BlockField(WOPL3MelodicBank, count=mrc.Ref('melodic_bank_count'))
    percussion_banks = mrc.BlockField(WOPL3PercussionBank, count=mrc.Ref('percussion_bank_count'))
