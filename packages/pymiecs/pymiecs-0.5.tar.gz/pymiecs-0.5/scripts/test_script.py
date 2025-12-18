# core-shell Mie coefficients for magnetizable media
# %%
"""TODO

- automatic nmax
- angular scattering
- implement VSH for:
    - external near-fields
    - internal fields

"""
# %%
import time

import numpy as np
import matplotlib.pyplot as plt
import pymiecs as mie
from PyMieScatt import MieQCoreShell, CoreShellScatteringFunction


wavelengths = np.linspace(400, 900, 100)  # wavelength in nm

r_core = 80.0
r_shell = r_core + 0.0

n_env = 1
n_core = 4
n_shell = 4

mu_env = 1
mu_core = 1
mu_shell = 1

n_max = 5
k0 = 2 * np.pi / wavelengths
k = k0 * n_env

a, b = mie.mie_coeff.core_shell_ab(
    k0,
    r_core,
    n_core,
    mu_core=1,
)

q_res = mie.Q(k0, r_core, n_core, r_shell, n_shell, mu_core=1, mu_shell=1)


theta, SL, SR, SU = mie.angular(
    k0,
    r_core,
    n_core,
    r_shell,
    n_shell,
    mu_core=1,
    mu_shell=1,
    angular_range=[0, np.pi * 1.0],
    angular_steps=36,
)
dteta = theta[1] - theta[0]

plt.plot(wavelengths, q_res["qsca"][0], label="own-scat")
plt.plot(
    wavelengths,
    (2 * SU * 2 / (k[:, None] ** 2 * r_shell**2)).mean(axis=1),
    label="angular-fwd",
)
# plt.plot(wavelengths, (SU).mean(axis=1)*5, label='angular-fwd-direct')
plt.legend()
plt.show()


# -- FW/BW
sca_diff_f = mie.Q_scat_differential(
    k,
    r_core,
    n_core,
    r_shell,
    n_shell,
    mu_core=1,
    mu_shell=1,
    angular_range=[0, np.pi / 20],
    angular_steps=15,
)
sca_diff_b = mie.Q_scat_differential(
    k,
    r_core,
    n_core,
    r_shell,
    n_shell,
    mu_core=1,
    mu_shell=1,
    angular_range=[19 * np.pi / 20, np.pi],
    angular_steps=15,
)
dteta = theta[1] - theta[0]

plt.plot(wavelengths, q_res["qfwd"][0], label="own-F")
plt.plot(wavelengths, q_res["qback"][0], label="own-B")

plt.plot(wavelengths, sca_diff_f["qsca"], label="angular-fwd", dashes=[2, 2])

plt.plot(
    wavelengths,
    sca_diff_b["qsca"],
    label="angular-bwd",
    dashes=[2, 2],
)

# plt.plot(1/wavelengths, np.abs(a[0]))
# plt.plot(1/wavelengths, np.abs(b[0]))
plt.legend()
plt.show()


# %%
angle_list = np.arcsin(np.linspace(0.01, 0.99, 20))
angle_list = np.linspace(0.01, np.pi, 20)
all_scat_fw = []
for angle_max in angle_list:
    sca_diff = mie.Q_scat_differential(k, r_core, n_core, angular_range=[0, angle_max])
    all_scat_fw.append(sca_diff["qsca"])

plt.imshow(
    all_scat_fw,
    extent=(wavelengths.min(), wavelengths.max(), angle_list.min(), angle_list.max()),
    aspect="auto",
)
plt.show()
#%%
sca_f = mie.Q_scat_differential(k, r_core, n_core, angular_range=[0, 0.01])
sca_fh = mie.Q_scat_differential(k, r_core, n_core, angular_range=[0, np.pi/2])
sca_b = mie.Q_scat_differential(k, r_core, n_core, angular_range=[24*np.pi/25, np.pi])
sca_bh = mie.Q_scat_differential(k, r_core, n_core, angular_range=[np.pi/2, np.pi])
plt.plot(wavelengths, sca_b['qsca'], label='BW - line')
plt.plot(wavelengths, sca_bh['qsca'], label='BW - hemisphere')
plt.plot(wavelengths, sca_f['qsca'], label='FW - line', dashes=[2,2])
plt.plot(wavelengths, sca_fh['qsca'], label='FW - hemisphere', dashes=[2,2])
plt.xlabel('wavelength (nm)')
plt.ylabel(r'Q_scat ($\sigma_{s}$ / $\sigma_{geo}$)')
plt.legend()
plt.show()


# %%
# --- compare to existing code


def get_spec_pymiescatt(n_core, n_shell, wavelengths, r_core, r_shell, n_env, n_max):
    q_sca = []
    q_abs = []
    q_fwd = []
    q_ratio = []
    for wl in wavelengths:
        Q_dict = MieQCoreShell(
            mCore=n_core,
            mShell=n_shell,
            wavelength=wl,
            dCore=2 * r_core,
            dShell=2 * r_shell,
            nMedium=n_env,
            asCrossSection=False,
            asDict=True,
        )
        q_sca.append(Q_dict["Qsca"])
        q_abs.append(Q_dict["Qabs"])
        q_ratio.append(Q_dict["Qratio"])
        try:
            q_fwd.append(Q_dict["Qfwd"])
        except KeyError:
            q_fwd.append(0)

    return np.array(q_sca), np.array(q_abs), np.array(q_ratio)


q_sca, q_abs, q_ratio = get_spec_pymiescatt(
    n_core, n_shell, wavelengths, r_core, r_shell, n_env, n_max=n_max
)

# plt.plot(wavelengths, q_res["qsca"][0], label="Qscat - own")
# plt.plot(wavelengths, q_sca, label="Qscat - pymiescatt", dashes=[2, 2])
# plt.xlabel("wavelength (nm)")
# plt.ylabel("Q scat")
# plt.legend(loc=2)

# plt.twinx()
# plt.plot(wavelengths, q_res["qback"][0] / q_res["qsca"][0], color="C3", label="own-bwd/scat")
# plt.plot(wavelengths, q_ratio, label="pyms ratio", color="C2", dashes=[2, 2])
# plt.ylabel("back / tot scat")
# plt.legend(loc=1)
# plt.show()


# # compare coefficients to pymiescatt

# ab_pms = ps.CoreShell.CoreShell_ab(mCore=n_core, mShell=n_shell,
#                          xCore = np.pi*2 * r_core/wl,
#     xShell = np.pi*2 * r_shell/wl)

# print(a)
# print(ab_pms[0][:len(a)])
# print("-------")
# print(b)
# print(ab_pms[1][:len(b)])


# %% test angular radiation
k_angular = k0[[3, 7, 12, 19, 29]]
k_angular = k0[60:90]
wl_angular = (2 * np.pi) / k_angular


def get_spec_pymiescatt_angular(n_core, n_shell, wavelengths, r_core, r_shell, n_env):
    SL_all = []
    SR_all = []
    SU_all = []
    for wl in wavelengths:
        theta, SL, SR, SU = CoreShellScatteringFunction(
            mCore=n_core,
            mShell=n_shell,
            wavelength=wl,
            dCore=2 * r_core,
            dShell=2 * r_shell,
            nMedium=n_env,
            minAngle=0,
            maxAngle=180,
            angularResolution=1,
        )
        SL_all.append(SL)
        SR_all.append(SR)
        SU_all.append(SU)

    return np.array(theta), np.array(SL_all), np.array(SR_all), np.array(SU_all)


t0 = time.time()
theta_all, SL_all, SR_all, SU_all = get_spec_pymiescatt_angular(
    n_core, n_shell, wl_angular, r_core, r_shell, n_env
)
t1 = time.time()
print("pymiescatt time ", t1 - t0)

theta, SL, SR, SU = mie.angular(
    k_angular, r_core, n_core, r_shell, n_shell, mu_core=1, mu_shell=1
)
t2 = time.time()
print("pymiecs time    ", t2 - t1)


plt.subplot(polar=True)
plt.plot(theta, SU.T, dashes=[4, 1])
plt.plot(theta_all, SU_all.T, dashes=[2, 2])
plt.show()
