import numpy as np
import matplotlib.pyplot as plt

import smuthi.simulation
import smuthi.initial_field
import smuthi.layers
import smuthi.postprocessing.far_field as ff

import pymiecs

from pyGDM2 import materials

from threadpoolctl import threadpool_limits

threadpool_limits(limits=8, user_api="blas")
import numba

numba.set_num_threads(8)


# config
wavelengths = np.linspace(400, 850, 81)
n_env = 1.0
n_subst = 1.0

r_core = 60.0
mat_core = pymiecs.materials.Silicon()
d_shell = 10.0
mat_shell = pymiecs.materials.Gold()

Z_offset_sphere = 1  # additional offset above substrate (nm)


# %% smuthi t-matrix simulations
scs_spec_tot = []
scs_spec_fw_int = []
scs_spec_bw_int = []
scs_spec_bw = []
scs_spec_fw = []
for wl in wavelengths:
    # Initialize the layer system
    two_layers = smuthi.layers.LayerSystem(
        thicknesses=[0, 0], refractive_indices=[n_subst, n_env]
    )

    # Scattering particle
    sphere_coreshell = pymiecs.t_matrix.SphereCoreShell(
        position=[0, 0, r_core + Z_offset_sphere],
        r_core=r_core,
        n_core=mat_core.get_refindex(wl),
        r_shell=r_core + d_shell,
        n_shell=mat_shell.get_refindex(wl),
        l_max=5,
    )

    # list of all scattering particles (only one in this case)
    particle_list = [sphere_coreshell]

    # eval s / p pol
    sc_tot_single_pol = []
    for pol in [0, 1]:
        sc_illum_cases = []
        for i_case in [0, 1]:
            # setup illumination & collection
            if i_case == 0:
                # backward
                angle_illumination = 0  # from top
                teta_list_collection = np.linspace(0.0, 0.01, 3)
                phi_list_collection = np.linspace(0, 2 * np.pi, 6)
            elif i_case == 1:
                # forward
                angle_illumination = 0  # from top
                teta_list_collection = np.linspace(np.pi - 0.01, np.pi, 3)
                phi_list_collection = np.linspace(0, 2 * np.pi, 6)

            # Initial field (normal incidence pw)
            plane_wave = smuthi.initial_field.PlaneWave(
                vacuum_wavelength=wl,
                polar_angle=angle_illumination,
                azimuthal_angle=0,
                polarization=pol,
            )  # 0=TE/s, 1=TM/p

            # Initialize and run simulation
            simulation = smuthi.simulation.Simulation(
                layer_system=two_layers,
                particle_list=particle_list,
                initial_field=plane_wave,
                log_to_terminal=False,
            )
            simulation.run()

            # evaluate the scattering
            # calculate and integrate farfield scattering
            ff_full = ff.scattering_cross_section(
                initial_field=plane_wave,
                particle_list=particle_list,
                layer_system=two_layers,
                azimuthal_angles=phi_list_collection,
                polar_angles=teta_list_collection,
            )

            # normalize by solid angle
            d_omega = np.sum(
                np.diff(teta_list_collection)[0]
                * np.diff(phi_list_collection)[0]
                * np.sin(teta_list_collection)
            )

            sc_illum_cases.append(np.sum(ff_full.integral()) / d_omega)
        sc_tot_single_pol.append(sc_illum_cases)
    scs_spec_tot.append(sc_tot_single_pol)
scs_spec_tot = np.array(scs_spec_tot)


# %% mie calculations
k0 = 2 * np.pi / wavelengths
q_mie = pymiecs.Q(
    k0,
    r_core=r_core,
    r_shell=r_core + d_shell,
    n_core=mat_core.get_refindex(wavelengths),
    n_shell=mat_shell.get_refindex(wavelengths),
    n_env=n_env,
)

# %% plot

plt.figure(figsize=(5, 3.5))
plt.title(
    "Si/Au core-shell sphere, r_c={}nm, r_s={}nm".format(r_core, r_core + d_shell)
)

plt.plot(wavelengths, np.mean(scs_spec_tot[..., 0], axis=1), label="fwd-smuthi")
plt.plot(wavelengths, np.mean(scs_spec_tot[..., 1], axis=1), label="back-smuthi")
plt.plot(
    wavelengths,
    q_mie["qfwd"][0] * q_mie["cs_geo"] / np.pi / 1.2,
    dashes=[2, 2],
    label="fwd-Mie",
)
plt.plot(
    wavelengths,
    q_mie["qback"][0] * q_mie["cs_geo"] / np.pi / 1.2,
    dashes=[2, 2],
    label="back-Mie",
)

plt.legend()
plt.xlabel("wavelength (nm)")
plt.ylabel("sigma scat")
plt.show()
