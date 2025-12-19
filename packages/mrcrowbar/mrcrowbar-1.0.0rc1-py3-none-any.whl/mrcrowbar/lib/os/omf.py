"""Tools for reading Relocatable Object Module Format (OMF) files.
source: https://pierrelib.pagesperso-orange.fr/exec_formats/OMF_v1.1.pdf
"""
from __future__ import annotations
from typing_extensions import Type

from mrcrowbar import models as mrc

class THEADR( mrc.Block ):
    name = mrc.StringField(length_field=mrc.UInt8)
    checksum = mrc.UInt8( mrc.Coda() )

class COMENT( mrc.Block ):
    type_id = mrc.UInt8()
    class_id = mrc.UInt8()
    data = mrc.Bytes()
    checksum = mrc.UInt8( mrc.Coda() )

class Address16( mrc.Block ):
    frame_is_thread = mrc.Bits( 0x00, 0b10000000 )
    frame = mrc.Bits( 0x00, 0b01110000 )
    target_is_thread = mrc.Bits( 0x00, 0b00001000 )
    skip_target_displacement = mrc.Bits( 0x00, 0b00000100 )
    target_thread = mrc.Bits( 0x00, 0b00000011 )
    
    @property
    def has_frame_datum( self ):
        return self.frame_is_thread == 0 and self.frame <= 2

    @property
    def has_target_datum( self ):
        return self.target_is_thread == 0

    @property
    def has_target_displacement( self ):
        return self.skip_target_displacement == 0 or (self.skip_target_displacement == 1 and self.target_is_thread == 1)

    frame_datum = mrc.UInt8( exists=mrc.Ref[bool]( 'has_frame_datum' ) )
    target_datum = mrc.UInt8( exists=mrc.Ref[bool]( 'has_target_datum' ) )
    target_displacement = mrc.UInt16_LE( exists=mrc.Ref[int]( 'has_target_displacement' ) )

class Address32( mrc.Block ):
    frame_is_thread = mrc.Bits( 0x00, 0b10000000 )
    frame = mrc.Bits( 0x00, 0b01110000 )
    target_is_thread = mrc.Bits( 0x00, 0b00001000 )
    skip_target_displacement = mrc.Bits( 0x00, 0b00000100 )
    target_thread = mrc.Bits( 0x00, 0b00000011 )
    
    @property
    def has_frame_datum( self ):
        return self.frame_is_thread == 0 and self.frame <= 2

    @property
    def has_target_datum( self ):
        return self.target_is_thread == 0

    @property
    def has_target_displacement( self ):
        return self.skip_target_displacement == 0 or (self.skip_target_displacement == 1 and self.target_is_thread == 1)

    frame_datum = mrc.UInt16_LE( exists=mrc.Ref[bool]( 'has_frame_datum' ) )
    target_datum = mrc.UInt16_LE( exists=mrc.Ref[bool]( 'has_target_datum' ) )
    target_displacement = mrc.UInt32_LE( exists=mrc.Ref[int]( 'has_target_displacement' ) )

class MODEND16( mrc.Block ):
    main = mrc.Bits( 0x00, 0b10000000 )
    start = mrc.Bits( 0x00, 0b01000000 )
    segment = mrc.Bits( 0x00, 0b00100000 )
    start_address = mrc.BlockField( Address16, exists=mrc.Ref[int]('start') ) 
    
    checksum = mrc.UInt8( mrc.Coda() )

class MODEND32( mrc.Block ):
    main = mrc.Bits( 0x00, 0b10000000 )
    start = mrc.Bits( 0x00, 0b01000000 )
    segment = mrc.Bits( 0x00, 0b00100000 )
    start_address = mrc.BlockField( Address32, exists=mrc.Ref[int]('start') ) 
    
    checksum = mrc.UInt8( mrc.Coda() )


class EXTDEF16Name( mrc.Block ):
    name = mrc.StringField( length_field=mrc.UInt8 )
    type_index = mrc.UInt8()

class EXTDEF16( mrc.Block ):
    names = mrc.BlockField( EXTDEF16Name, stream=True )
    checksum = mrc.UInt8( mrc.Coda() ) 

class EXTDEF32Name( mrc.Block ):
    name = mrc.StringField( length_field=mrc.UInt8 )
    type_index = mrc.UInt16_LE()

class EXTDEF32( mrc.Block ):
    names = mrc.BlockField( EXTDEF32Name, stream=True )
    checksum = mrc.UInt8( mrc.Coda() ) 

class PUBDEF16Name( mrc.Block ):
    name = mrc.StringField( length_field=mrc.UInt8 )
    public_offset = mrc.UInt16_LE()
    type_index = mrc.UInt8()

class PUBDEF16( mrc.Block ):
    base_group_index = mrc.UInt8()
    base_segment_index = mrc.UInt8()

    @property
    def manual( self ) -> bool:
        return self.base_segment_index == 0

    base_frame =  mrc.UInt16_LE( exists=mrc.ConstRef[bool]( 'manual' ) )
    names = mrc.BlockField( PUBDEF16Name, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class PUBDEF32Name( mrc.Block ):
    name = mrc.StringField( length_field=mrc.UInt8 )
    public_offset = mrc.UInt32_LE()
    type_index = mrc.UInt16_LE()

class PUBDEF32( mrc.Block ):
    base_group_index = mrc.UInt16_LE()
    base_segment_index = mrc.UInt16_LE()

    @property
    def manual( self ) -> bool:
        return self.base_segment_index == 0

    base_frame =  mrc.UInt16_LE( exists=mrc.ConstRef[bool]( 'manual' ) )
    names = mrc.BlockField( PUBDEF32Name, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class LNAMES( mrc.Block ):
    names = mrc.StringField(length_field=mrc.UInt8, stream=True)
    checksum = mrc.UInt8( mrc.Coda() )

class SEGDEF16( mrc.Block ):
    alignment = mrc.Bits( 0, bits=0b11100000 )
    combination = mrc.Bits( 0, bits=0b00011100 )
    high_order = mrc.Bits( 0, bits=0b00000010 )
    use_32 = mrc.Bits( 0, bits=0b00000001 )

    @property
    def manual( self ) -> bool:
        return self.alignment == 0

    frame_number = mrc.UInt16_LE( exists=mrc.ConstRef[bool]( 'manual' ) )
    offset = mrc.UInt8( exists=mrc.ConstRef[bool]( 'manual' ) )
    segment_length = mrc.UInt16_LE()
    segment_name_index = mrc.UInt8()
    class_name_index = mrc.UInt8()
    overlay_name_index = mrc.UInt8()
    checksum = mrc.UInt8( mrc.Coda() )


class SEGDEF32( mrc.Block ):
    alignment = mrc.Bits( 0, bits=0b11100000 )
    combination = mrc.Bits( 0, bits=0b00011100 )
    high_order = mrc.Bits( 0, bits=0b00000010 )
    use_32 = mrc.Bits( 0, bits=0b00000001 )

    @property
    def manual( self ) -> bool:
        return self.alignment == 0

    frame_number = mrc.UInt16_LE( exists=mrc.ConstRef[bool]( 'manual' ) )
    offset = mrc.UInt8( exists=mrc.ConstRef[bool]( 'manual' ) )
    segment_length = mrc.UInt32_LE()
    segment_name_index = mrc.UInt16_LE()
    class_name_index = mrc.UInt16_LE()
    overlay_name_index = mrc.UInt16_LE()
    checksum = mrc.UInt8( mrc.Coda() )

class GRPDEF16Record( mrc.Block ):
    ff_index = mrc.UInt8()
    segment_definition = mrc.UInt8()

class GRPDEF16( mrc.Block ):
    group_name_index = mrc.UInt8()
    records = mrc.BlockField( GRPDEF16Record, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class THREAD16( mrc.Block ):
    type_flag = mrc.Const( mrc.Bits( 0x00, 0b10000000 ), 0 )
    is_frame = mrc.Bits( 0x00, 0b01000000 )
    unused = mrc.Bits( 0x00, 0b00100000 )
    method = mrc.Bits( 0x00, 0b00011100 )
    thread = mrc.Bits( 0x00, 0b00000011 )
    index = mrc.UInt8( 0x01 )

class THREAD32( mrc.Block ):
    type_flag = mrc.Const( mrc.Bits( 0x00, 0b10000000 ), 0 )
    is_frame = mrc.Bits( 0x00, 0b01000000 )
    unused = mrc.Bits( 0x00, 0b00100000 )
    method = mrc.Bits( 0x00, 0b00011100 )
    thread = mrc.Bits( 0x00, 0b00000011 )
    index = mrc.UInt16_LE( 0x01 )

class FIXUP16( mrc.Block ):
    type_flag = mrc.Const( mrc.Bits16( 0x00, 0b1000000000000000 ), 1 ) 
    segment_relative = mrc.Bits16( 0x00, 0b0100000000000000 )
    location = mrc.Bits16( 0x00, 0b0011110000000000 )
    record_offset = mrc.Bits16( 0x00, 0b0000001111111111 )
    address = mrc.BlockField( Address16 )

class FIXUP32( mrc.Block ):
    type_flag = mrc.Const( mrc.Bits16( 0x00, 0b1000000000000000 ), 1 ) 
    segment_relative = mrc.Bits16( 0x00, 0b0100000000000000 )
    location = mrc.Bits16( 0x00, 0b0011110000000000 )
    record_offset = mrc.Bits16( 0x00, 0b0000001111111111 )
    address = mrc.BlockField( Address32 )


class FIXUPRecord16( mrc.Block ):
    type_flag = mrc.Bits( 0x00, 0b10000000 )

    @property
    def is_thread( self ) -> bool:
        return self.type_flag == 0

    @property
    def is_fixup( self ) -> bool:
        return self.type_flag == 1

    thread = mrc.BlockField( THREAD16, 0x00, exists = mrc.ConstRef[bool]( 'is_thread' ) )
    fixup = mrc.BlockField( FIXUP16, 0x00, exists=mrc.ConstRef[bool]( 'is_fixup' ) )

class FIXUPRecord32( mrc.Block ):
    type_flag = mrc.Bits( 0x00, 0b10000000 )

    @property
    def is_thread( self ) -> bool:
        return self.type_flag == 0

    @property
    def is_fixup( self ) -> bool:
        return self.type_flag == 1

    is_frame = mrc.Bits( 0x00, 0b01000000, exists=mrc.ConstRef[bool]( 'is_thread' ) )
    thread = mrc.BlockField( THREAD32, 0x00, exists = mrc.ConstRef[bool]( 'is_thread' ) )
    fixup = mrc.BlockField( FIXUP32, 0x00, exists=mrc.ConstRef[bool]( 'is_fixup' ) )

class FIXUPP16( mrc.Block ):
    records = mrc.BlockField( FIXUPRecord16, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class FIXUPP32( mrc.Block ):
    records = mrc.BlockField( FIXUPRecord32, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class LEDATA16( mrc.Block ):
    segment_index = mrc.UInt8()
    enumerated_data_offset = mrc.UInt16_LE()
    data = mrc.Bytes()
    checksum = mrc.UInt8( mrc.Coda() )

class LEDATA32( mrc.Block ):
    segment_index = mrc.UInt16_LE()
    enumerated_data_offset = mrc.UInt32_LE()
    data = mrc.Bytes()
    checksum = mrc.UInt8( mrc.Coda() )

class DataBlock16( mrc.Block ):
    repeat_count = mrc.UInt16_LE()
    block_count = mrc.UInt16_LE()

    @property
    def is_bytes( self ) -> bool:
        return self.block_count == 0

    content = mrc.StringField( length_field=mrc.UInt8, exists=mrc.ConstRef('is_bytes') )
    blocks = mrc.BlockField( "self", count=mrc.Ref('block_count'))

class LIDATA16( mrc.Block ):
    segment_index = mrc.UInt8()
    iterated_data_offset = mrc.UInt16_LE()
    blocks = mrc.BlockField( DataBlock16, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class DataBlock32( mrc.Block ):
    repeat_count = mrc.UInt32_LE()
    block_count = mrc.UInt16_LE()

    @property
    def is_bytes( self ) -> bool:
        return self.block_count == 0

    content = mrc.StringField( length_field=mrc.UInt8, exists=mrc.ConstRef('is_bytes') )
    blocks = mrc.BlockField( "self", count=mrc.Ref('block_count'))

class LIDATA32( mrc.Block ):
    segment_index = mrc.UInt16_LE()
    iterated_data_offset = mrc.UInt32_LE()
    blocks = mrc.BlockField( DataBlock32, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class LEXTDEF16( EXTDEF16 ):
    pass

class LEXTDEF32( EXTDEF32 ):
    pass

class LPUBDEF16( PUBDEF16 ):
    pass

class LPUBDEF32( PUBDEF32 ):
    pass

class CEXTDEFRecord( mrc.Block ):
    logical_name_index = mrc.UInt8()
    type_index = mrc.UInt8()

class CEXTDEF( mrc.Block ):
    records = mrc.BlockField( CEXTDEFRecord, stream=True )
    checksum = mrc.UInt8( mrc.Coda() )

class COMDAT16( mrc.Block ):
    continuation = mrc.Bits( 0x00, 0b00000001 )
    iterated_data = mrc.Bits( 0x00, 0b00000010 )
    local = mrc.Bits( 0x00, 0b00000100 )
    data_in_code_segment = mrc.Bits( 0x00, 0b00001000 )

    selection_criteria = mrc.Bits( 0x01, 0b11110000 )
    allocation_type = mrc.Bits( 0x01, 0b00001111 )
    align = mrc.UInt8()
    enumerated_data_offset = mrc.UInt16_LE()
    type_index_field = mrc.UInt8()
    public_base = mrc.UInt8()
    public_name_index = mrc.UInt8()
    data = mrc.Bytes()
    checksum = mrc.UInt8( mrc.Coda() )

class COMDAT32( mrc.Block ):
    continuation = mrc.Bits( 0x00, 0b00000001 )
    iterated_data = mrc.Bits( 0x00, 0b00000010 )
    local = mrc.Bits( 0x00, 0b00000100 )
    data_in_code_segment = mrc.Bits( 0x00, 0b00001000 )

    selection_criteria = mrc.Bits( 0x01, 0b11110000 )
    allocation_type = mrc.Bits( 0x01, 0b00001111 )
    align = mrc.UInt8()
    enumerated_data_offset = mrc.UInt32_LE()
    type_index_field = mrc.UInt16_LE()
    public_base = mrc.UInt16_LE()
    public_name_index = mrc.UInt16_LE()
    data = mrc.Bytes()
    checksum = mrc.UInt8( mrc.Coda() )

class LibraryHeaderRecord( mrc.Block ):
    dict_offset = mrc.UInt32_LE()
    dict_size = mrc.UInt16_LE()
    flags = mrc.UInt8()
    padding = mrc.Bytes()


class LibraryEndRecord( mrc.Block ):
    padding = mrc.Bytes()


class OMF( mrc.Block ):
    CHUNKS: dict[int, type[mrc.Block]] = {
        0x80: THEADR,
        0x88: COMENT,
        0x8a: MODEND16,
        0x8b: MODEND32,
        0x8c: EXTDEF16,
        0x8d: EXTDEF32,
        0x90: PUBDEF16,
        0x91: PUBDEF32,
        0x96: LNAMES,
        0x98: SEGDEF16,
        0x99: SEGDEF32,
        0x9a: GRPDEF16,
        0x9c: FIXUPP16,
        0x9d: FIXUPP32,
        0xa0: LEDATA16,
        0xa1: LEDATA32,
        0xa2: LIDATA16,
        0xa3: LIDATA32,
        0xb4: LEXTDEF16,
        0xb5: LEXTDEF32,
        0xb6: LPUBDEF16,
        0xb7: LPUBDEF32,
        0xbc: CEXTDEF,
        0xc2: COMDAT16,
        0xc3: COMDAT32,
        0xf0: LibraryHeaderRecord,
        0xf1: LibraryEndRecord,
    }
    chunks = mrc.ChunkField(CHUNKS, id_field=mrc.UInt8, length_field=mrc.UInt16_LE, default_klass=mrc.Unknown, fill=b'\x00')
