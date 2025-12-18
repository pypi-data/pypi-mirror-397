"""
example demonstrating basic usage of pymiecs

author: P. Wiecha, 11/2024
"""

# %%
import time

import numpy as np
import matplotlib.pyplot as plt
import pymiecs as mie
from PyMieScatt import MieQCoreShell, CoreShellScatteringFunction

# - setup a core-shell sphere
wavelengths = np.linspace(400, 900, 100)  # wavelength in nm
k0 = 2 * np.pi / wavelengths

r_core = 100.0
r_shell = r_core + 10.0

n_env = 1
mat_core = mie.materials.MaterialDatabase("Si")
mat_shell = mie.materials.MaterialDatabase("Au")
n_core = mat_core.get_refindex(wavelength=wavelengths)
n_shell = mat_shell.get_refindex(wavelength=wavelengths)


# %% Mie coefficients
a, b = mie.mie_coeff.core_shell_ab(
    k0, r_core=r_core, n_core=n_core, r_shell=r_shell, n_shell=n_shell, n_max=3
)

# - plot Mie coefficients
colors_blue = plt.cm.Blues(np.linspace(0.4, 1, len(a)))
colors_red = plt.cm.Reds(np.linspace(0.4, 1, len(a)))

plt.figure(figsize=(10, 4))

plt.subplot(121)
for i, spec in enumerate(a):
    plt.plot(wavelengths, spec.real, label=f"Re(a_{i+1})", color=colors_blue[i])
for i, spec in enumerate(b):
    plt.plot(wavelengths, spec.real, label=f"Re(b_{i+1})", color=colors_red[i])
plt.legend(ncol=2)
plt.xlabel("wavelength (nm)")

plt.subplot(122)
for i, spec in enumerate(a):
    plt.plot(wavelengths, spec.imag, label=f"Im(a_{i+1})", color=colors_blue[i])
for i, spec in enumerate(b):
    plt.plot(wavelengths, spec.imag, label=f"Im(b_{i+1})", color=colors_red[i])
plt.legend(ncol=2)
plt.xlabel("wavelength (nm)")
plt.tight_layout()
plt.show()


# %% efficiencies

# - calculate efficiencies
q_res = mie.Q(k0, r_core=r_core, n_core=n_core, r_shell=r_shell, n_shell=n_shell)

# - plot
plt.plot(wavelengths, q_res["qsca"], label="scat")
plt.plot(wavelengths, q_res["qabs"], label="abs.")
plt.plot(wavelengths, q_res["qext"], label="extinct")

plt.legend()
plt.xlabel("wavelength (nm)")
plt.ylabel(r"efficiency (1/$\sigma_{geo}$)")
plt.tight_layout()
plt.show()


# %% differential cross sections

# -- FW/BW
sca_diff_f = mie.Q_scat_differential(
    k0,
    r_core,
    n_core,
    r_shell,
    n_shell,
    mu_core=1,
    mu_shell=1,
    angular_range=[0, np.pi / 200],
    angular_steps=2,
)
sca_diff_b = mie.Q_scat_differential(
    k0,
    r_core,
    n_core,
    r_shell,
    n_shell,
    mu_core=1,
    mu_shell=1,
    angular_range=[199 * np.pi / 200, np.pi],
    angular_steps=2,
)

plt.plot(wavelengths, q_res["qfwd"], label="forward")
plt.plot(wavelengths, q_res["qback"], label="backward")

plt.plot(wavelengths, sca_diff_f["qsca"], label="angular-fwd", dashes=[2, 2])
plt.plot(wavelengths, sca_diff_b["qsca"], label="angular-bwd", dashes=[2, 2])


plt.legend()
plt.xlabel("wavelength (nm)")
plt.ylabel("differential scattering (a.u.)")
plt.legend()
plt.show()


# %% angular scattering
k_angular = k0[::10]
wls_angular = 2 * np.pi / k_angular
n_core_wls_angular = mat_core.get_refindex(wavelength=wls_angular)
n_shell_wls_angular = mat_shell.get_refindex(wavelength=wls_angular)
theta, I_s, I_p, I_unpol = mie.angular(
    k_angular,
    r_core=r_core,
    n_core=n_core_wls_angular,
    r_shell=r_shell,
    n_shell=n_shell_wls_angular,
)

plt.subplot(polar=True)
plt.plot(theta, I_unpol.T, dashes=[4, 1])
plt.show()
