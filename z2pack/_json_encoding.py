#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.04.2016 10:21:56 CEST
# File:    _json_encoding.py

import json
import numbers
from functools import singledispatch
from collections.abc import Iterable

import numpy as np
from fsc.export import export

from .surface._result import SurfaceResult
from .surface._data import SurfaceData, SurfaceLine
from .line import LineResult, OverlapLineData, EigenstateLineData

@export
@singledispatch
def encode(obj):
    raise TypeError('cannot JSONify {} object {}'.format(type(obj), obj))

@encode.register(bool)
@encode.register(np.bool_)
def _(obj):
    return bool(obj)

@encode.register(numbers.Integral)
def _(obj):
    return int(obj)

@encode.register(numbers.Real)
def _(obj):
    return float(obj)
    
@encode.register(numbers.Complex)
def _(obj):
    return dict(__complex__=True, real=encode(obj.real), imag=encode(obj.imag))

@encode.register(str)
def _(obj):
    return obj

@encode.register(Iterable)
def _(obj):
    return list(obj)

@encode.register(EigenstateLineData)
def _(obj):
    return dict(
        __eigenstate_line_data__=True,
        eigenstates=encode(obj.eigenstates)
    )

@encode.register(OverlapLineData)
def _(obj):
    return dict(
        __overlap_line_data__=True,
        overlaps=encode(obj.overlaps)
    )
    
@encode.register(LineResult)
def _(obj):
    return dict(
        __line_result__=True,
        data=encode(obj.data),
        ctrl_convergence=obj.ctrl_convergence,
        ctrl_states=obj.ctrl_states
    )

@encode.register(SurfaceLine)
def _(obj):
    return dict(
        __surface_line__=True,
        t=obj.t,
        result=encode(obj.result)
    )

@encode.register(SurfaceData)
def _(obj):
    return dict(
        __surface_data__=True,
        lines=encode(obj.lines)
    )

@encode.register(SurfaceResult)
def _(obj):
    return dict(
        __surface_result__=True,
        data=encode(obj.data),
        ctrl_convergence=obj.ctrl_convergence,
        ctrl_states=obj.ctrl_states
    )

#-----------------------------------------------------------------------#

@export
@singledispatch
def decode(obj):
    return obj

@decode.register(str)
def _(obj):
    return obj

@decode.register(Iterable)
def _(obj):
    return [decode(x) for x in obj]

def decode_surface_result(obj):
    # The states / convergence of the controls are set manually
    res = SurfaceResult(obj['data'], [], [])
    res.ctrl_convergence = decode(obj['ctrl_convergence'])
    res.ctrl_states = decode(obj['ctrl_states'])
    return res

def decode_surface_data(obj):
    return SurfaceData(decode(obj['lines']))

def decode_surface_line(obj):
    return SurfaceLine(obj['t'], decode(obj['result']))

def decode_line_result(obj):
    # The states / convergence of the controls are set manually
    res = LineResult(obj['data'], [], [])
    res.ctrl_convergence = decode(obj['ctrl_convergence'])
    res.ctrl_states = decode(obj['ctrl_states'])
    return res

def decode_overlap_line_data(obj):
    return EigenstateLineData(obj['overlaps'])

def decode_eigenstate_line_data(obj):
    return EigenstateLineData(obj['eigenstates'])

def decode_complex(obj):
    return complex(obj['real'], obj['imag'])


@decode.register(dict)
def _(obj):
    special_markers = [key for key in obj.keys() if key.startswith('__')]
    if len(special_markers) == 1:
        name = special_markers[0].strip('__')
        return globals()['decode_' + name](obj)
    else:
        return obj
