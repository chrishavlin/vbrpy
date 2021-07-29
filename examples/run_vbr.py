from vbrpy import vbr_helper
import numpy as np
import matplotlib.pyplot as plt

d_cm = 1.
d_m = d_cm / 100.
d_um = d_m * 1e6

field_dict = dict(
    T = vbr_helper.Field('T_K',
                         'transpose(linspace(300, 1600, 100))',
                         np.linspace(300, 1600, 100)
                         ),
    P = vbr_helper.Field('P_GPa', 'transpose(linspace(0, 3, 100))', np.linspace(0, 3, 100)),
    phi = vbr_helper.Field('phi', '0.01 * ones(100,1)', np.ones((100,))),
    d = vbr_helper.Field('d_um', f"{d_um} * ones(100,1)", d_um * np.ones((100,))),
    rho = vbr_helper.Field('rho', '3300 * ones(100,1)', 3300 * np.ones((100,))),
    f =  vbr_helper.Field('f', '[0.01, 0.1]', np.array([0.01, 0.1]))
)

SVs = vbr_helper.StateVars()
for f in field_dict.values():
    SVs.add_field(f)


vbr = vbr_helper.VBR(SVs)
vbr.add_method('elastic', 'anharmonic')
# vbr.generate_mfile()
vbr.mat_out = "vbr_output.mat"
# to save a file
vbr.mfile_name = './temphello.m'
vbr.save_mfile()
vbr.run_mfile()

Vs = vbr.out.elastic.anharmonic.Vsu/1e3

plt.plot(Vs, vbr.SVs.T_K.values)
