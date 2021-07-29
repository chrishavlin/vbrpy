from dask import delayed, array
import numpy as np
from numpy.typing import ArrayLike
from typing import Optional, Union
from collections import OrderedDict
import subprocess
import os
from scipy import io

class Field():
    def __init__(self, field: str, valstr: str, values: ArrayLike):
        self.field = field
        self.valstr = valstr
        self.values = values
        self._mstr = f"{field} = {valstr};"


class StateVars():

    T_K = None
    d_um = None
    phi = None
    P_GPa = None
    rho = None
    f_Hz = None


    def __init__(self):
        self.field_list = []


    def add_field(self, field: Field):
        setattr(self, field.field, field)
        self.field_list.append(field.field)



class VBR():

    _mfile_text = None
    mfile_name = None
    _octave = True
    out = None
    mat_out = 'mfile_results.mat'

    def __init__(self, SVs: StateVars):
        self.SVs = SVs
        self.vbr_path = '/home/chris/src/vbr/' #os.environ['vbr_']

        for ty in ['elastic', 'viscous', 'anelastic']:
            setattr(self, f"{ty}_methods", [])



    def add_method(self, method_type: str, method_str: str):
        mlist = getattr(self, f"{method_type}_methods")
        mlist.append(method_str)
        setattr(self, f"{method_type}_methods", mlist)

    @property
    def mfile_text(self):
        self.generate_mfile()
        return self._mfile_text

    def _m_header(self, m_str: list):
        m_str.append('% auto-generated mfile for VBR!')
        m_str.append(' ')
        m_str.append('% add VBR to the path')
        m_str.append('clear;')
        m_str.append(f"addpath('{self.vbr_path}');")
        m_str.append('vbr_init')
        m_str.append(' ')
        return m_str

    def _m_methods(self, m_str: list):
        for m in  ['elastic', 'viscous', 'anelastic']:
            mlist = getattr(self, m+'_methods')
            if mlist:
                estr = ';'.join([f"'{v}'" for v in mlist])
                estr = "VBR.in." + m + ".methods_list = {" + estr + "};"
                m_str.append(estr)
            m_str.append(" ")
        return m_str

    def _m_svs(self, m_str: list):
        for fl in self.SVs.field_list:
            field = getattr(self.SVs, fl)
            m_str.append(f"VBR.in.SV.{field._mstr}")
        return m_str

    def _m_run_save(self, m_str: list):
        m_str.append(" ")
        m_str.append("VBR = VBR_spine(VBR);")
        m_str.append("VBRout.input = VBR.in;")
        m_str.append("VBRout.out = VBR.out;")
        if self._octave:
            m_str.append('save("' + self.mat_out + '", "-struct", "VBRout", "-mat-binary");')
        return m_str

    def generate_mfile(self):
        m_str = self._m_header([])
        m_str = self._m_methods(m_str)
        m_str = self._m_svs(m_str)
        m_str = self._m_run_save(m_str)
        self._mfile_text = m_str

    def save_mfile(self, mfile_name: Optional[str] = None):
        if mfile_name:
            self.mfile_name = mfile_name
        elif self.mfile_name:
            mfile_name = self.mfile_name
        else:
            raise ValueError("must provide mfile_name or set mfile_name attr prior to call.")

        with open(mfile_name, 'w') as fi:
            for ln in self.mfile_text:
                fi.write(ln+"\n")

    def run_mfile(self):

        if os.path.isfile(self.mat_out) is False:
            self.save_mfile()
            if self._octave:
                spargs = ["octave", "--no-gui", self.mfile_name]
            else:
                raise NotImplementedError("octave only for now")
            subprocess.run(spargs)

        self.load_results()


    def load_results(self):

        m = io.loadmat(self.mat_out,
                       uint16_codec='ascii',
                       struct_as_record=False,
                       squeeze_me=True)

        setattr(self, 'out', m['out'])
