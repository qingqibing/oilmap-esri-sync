import os
import struct
from collections import OrderedDict

def read_lu3(data):
    """Return a dictionary of arrays with data from the LU3 file
    :param bytes data: LU3 file in binary form"""

    rec = OrderedDict([
        ("Version", []), ("Simtime",[]), ("Time",   []), ("rec1st",[]), ("rec2st",[]), ("rec2end",[]),
        ("rec3st",[]), ("rec3end",[]), ("rec5st",[]), ("rec5end",[]), ("sed2st",[]), ("sed2end",[]),
        ("rar1st",[]), ("rar1end",[]), ("rth1st",[]), ("rth1end",[]), ("rsf1st",[]), ("rsf1end",[]),
        ("rsp1st",[]), ("rsp1end",[]), ("rss1st",[]), ("rss1end",[]), ("rat1st",[]), ("rat1end",[]),
    ])

    i = True
    while(i):
        try:
            for k in rec.keys():
                rec[k].append(struct.unpack('i' if k!="Time" else 'f', data.read(4))[0]) # one float value
        except struct.error:
            i = False
    return rec


def read_slk(lu3rec, data):
    """Read SLK data from binary form by using a struct to unpack the bytes. Creates an array:
    [
        (time0, [ [ihab_rec0, dx_rec0, dy_rec0, LON_rec0, LAT_rec0, v1_rec0, v2_rec0, v3_rec0, v4_rec0], [...] ]),
        (time1, [...]),
        ...
        (timeN, ...)
    ]
    All SLK variables are floats.
    :param dict lu3rec: record of byte offsets from LU3 file, corresponding to each time step record
    :param bytes data: SLK file read in binary form"""

    fields = ["ihab", "dx", "dy", "LON", "LAT", "v1", "v2", "v3", "v4"]
    fstart = lu3rec['rss1st'][0] * 36 # number of records * record size = byte offset to start at
    data.seek(fstart)

    slk_out = []
    recs = zip(lu3rec['rss1st'], lu3rec['rss1end'], lu3rec['Time'])
    for (start, end, time) in recs:
        try:
            tstep_out = []
            for _rec in range(end-start+1):
                _rec_out = []
                for k in fields:
                    _rec_out.append(struct.unpack('f', data.read(4))[0]) # all floats
                tstep_out.append(_rec_out)
            if tstep_out: # where the range is 0 (start==end), we don't need to append any records
                slk_out.append((time, tstep_out))
        except struct.error:
            break

    return slk_out


def read_tr3(lu3rec, data):
    """Read TR3 data from binary form by using a struct to unpack the bytes. Creates two arrays:
    [ # spillets
        (time0, [ [xspil, yspil, ... spilletNumber], [...] ]),
        (time1, [...]),
        ...
        (timeN, ...)
    ]
    [ # shoreline
        (time0, [ [ICellIndex, JCellIndex, ...], [...] ]),
        (time1, [...]),
        ...
        (timeN, ...)
    ]
    Spillets have only two integer variables: ptype and spilletNumber; the rest are floats.
    Shoreline data has 3 integer variables: ICellIndex, JCellIndex, and shoretype. The rest are floats.
    :param dict lu3rec: record of byte offsets from LU3 file, corresponding to each time step record
    :param bytes data: TR3 file read in binary form"""

    fields_spl = ["xspil", "yspil", "rspil", "xspilold", "yspilold", "ptype", "surf", "dspilm", "viscm", "fwc", "age", "spilletNumber"]
    fields_shr = ["ICellIndex", "JCellIndex", "shoretype", "ShoreArea", "ShoreLength", "ShoreViscosity", "SegmentLon1",
                  "SegmentLat1", "SegmentLon2", "SegmentLat2", "ShoreMass", "ex2"]

    fstart = lu3rec['rec2st'][0] * 48 # number of records * bytes per record = byte offset
    data.seek(fstart)                 # seek to the beginning of records

    recs_out_spl = [] # array [(time, record_array), ...]
    recs_out_shr = []

    # loop through timestep, index position groups
    for (rec2st, rec2end, rec3st, rec3end, time) in zip(lu3rec['rec2st'], lu3rec['rec2end'], lu3rec['rec3st'], lu3rec['rec3end'], lu3rec['Time']):
        try:
            # spillets---
            tstep_records_spl = []                         # hold all spillet records for *this* timestamp
            for _rec in range(rec2end-rec2st):             # obtain this many records for this timestep
                _rec_out = []
                for k in fields_spl:
                    _rec_out.append(struct.unpack('f' if k not in ["ptype", "spilletNumber"] else 'i', data.read(4))[0])
                tstep_records_spl.append(_rec_out)         # append the newly created record               
            recs_out_spl.append((time, tstep_records_spl)) # append all records for this timestep

            # seek to the starting index of rec3st for *this* timestamp
            data.seek(rec3st * 48)
            
            # shoreline--- same steps as spillets
            tstep_records_shr = []
            for _rec in range(rec3end-rec3st):
                _rec_out = []
                for k in fields_shr:
                    _rec_out.append(struct.unpack('f' if k not in ["ICellIndex", "JCellIndex", "shoretype"] else 'i', data.read(4))[0])
                tstep_records_shr.append(_rec_out)
            recs_out_shr.append((time, tstep_records_shr))

            data.read(48*7) # blank group between timestep-groups of 7 bytes, which we must multiply by 48 (size of each record)

        except struct.error:
            break
    return (recs_out_spl, recs_out_shr)
