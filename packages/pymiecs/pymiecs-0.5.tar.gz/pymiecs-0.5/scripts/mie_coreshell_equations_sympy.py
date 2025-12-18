# core-shell Mie coefficients for magnetizable media
import numpy as np
import sympy as sp
from sympy import Symbol, symbols, solve


an = Symbol("an")
bn = Symbol("bn")
cn = Symbol("cn")
dn = Symbol("dn")
fn = Symbol("fn")
gn = Symbol("gn")
vn = Symbol("vn")
wn = Symbol("wn")

# refindex. assume m of environment to be 1 (others are relative)
m1 = Symbol("m1")
m2 = Symbol("m2")
# permeability
# mu = 1.0  # environemnt
mu = Symbol("mu")  # environemnt
mu1 = Symbol("mu1")
mu2 = Symbol("mu2")

psin1x = Symbol("psin1x")
psibn1x = Symbol("psibn1x")

psin2x = Symbol("psin2x")
psibn2x = Symbol("psibn2x")
chin2x = Symbol("chin2x")
chibn2x = Symbol("chibn2x")

psin2y = Symbol("psin2y")
psibn2y = Symbol("psibn2y")
chin2y = Symbol("chin2y")
chibn2y = Symbol("chibn2y")

xiny = Symbol("xiny")
xibny = Symbol("xibny")
psiny = Symbol("psiny")
psibny = Symbol("psibny")


# solve Mie equations (Bohren Huffmann, chap 8.1 page 183)
eq1 = fn * m1 * psin2x - vn * m1 * chin2x - cn * m2 * psin1x
eq2 = wn * m1 * chibn2x - gn * m1 * psibn2x + dn * m2 * psibn1x
eq3 = vn * mu1 * chibn2x - fn * mu1 * psibn2x + cn * mu2 * psibn1x
eq4 = gn * mu1 * psin2x - wn * mu1 * chin2x - dn * mu2 * psin1x

eq5 = m2 * psibny - an * m2 * xibny - gn * psibn2y + wn * chibn2y
eq6 = m2 * bn * xiny - m2 * psiny + fn * psin2y - vn * chin2y
eq7 = mu2 * psiny - an * mu2 * xiny - gn * mu * psin2y + wn * mu * chin2y
eq8 = bn * mu2 * xibny - mu2 * psibny + fn * mu * psibn2y - vn * mu * chibn2y

s_mie = solve(
    [
        eq1,
        eq2,
        eq3,
        eq4,
        eq5,
        eq6,
        eq7,
        eq8,
    ],
    [an, bn, cn, dn, fn, gn, vn, wn],
    dict=True,
)

print("{} solution(s) found:".format(len(s_mie)))
for k in s_mie[0]:
    print(k, s_mie[0][k])
an_formula = sp.simplify(s_mie[0][an])
bn_formula = sp.simplify(s_mie[0][bn])


# %%
print("{}:".format(an))
print(an_formula)
print(sp.latex(an_formula))

print("{}:".format(bn))
print(bn_formula)


# %% evaluate
from scipy import special

def riccati_j_n(n, x):
    # riccati-bessel of the first kind and its derivative
    jn = special.spherical_jn(n, x)
    jnp = special.spherical_jn(n, x, derivative=True)
    return np.array([x * jn, jn + x * jnp])


def riccati_y_n(n, x):
    # riccati-bessel of the second kind and its derivative
    yn = special.spherical_yn(n, x)
    ynp = special.spherical_yn(n, x, derivative=True)

    return np.array([-1 * x * yn, -1 * (yn + x * ynp)])


def riccati_h1_n(n, x):
    # riccati-bessel for hankel function and its derivative
    # For the identity, see https://en.wikipedia.org/wiki/Bessel_function
    return riccati_j_n(n, x) - 1j * riccati_y_n(n, x)


wl = 500.0  # wavelength in nm

r_core = 80.0
r_shell = r_core + 100.0

n_env = 1
n_core = 4
n_shell = 0.1   + .7j

mu_env = 1
mu_core = 1
mu_shell = 1





# --- Test: evaluate sympy formula
# n = 1  # coefficient order

# # - pre-evaluation
# n1 = n_core / n_env
# n2 = n_shell / n_env
# k = 2 * np.pi / (wl / n_env)
# x = k * r_core
# y = k * r_shell

# # - special functions:
# # psi_n = z * j_n(z)   --> riccati_j_n
# # chi_n = -z * y_n(z)  --> riccati_y_n
# # xi_n = z * h1_n(z)   --> riccati_h1_n

# rj1x = riccati_j_n(n, n1 * x)
# rj2x = riccati_j_n(n, n2 * x)
# rjy = riccati_j_n(n, y)
# rj2y = riccati_j_n(n, n2 * y)

# ry2x = riccati_y_n(n, n2 * x)
# ry2y = riccati_y_n(n, n2 * y)

# rh1y = riccati_h1_n(n, y)

# values = dict(
#     m1=n1,
#     m2=n2,
#     mu=mu_env,
#     mu1=mu_core,
#     mu2=mu_shell,
#     psin1x=rj1x[0],
#     psibn1x=rj1x[1],
#     psin2x=rj2x[0],
#     psibn2x=rj2x[1],
#     psiny=rjy[0],
#     psibny=rjy[1],
#     psin2y=rj2y[0],
#     psibn2y=rj2y[1],
#     chin2x=ry2x[0],
#     chibn2x=ry2x[1],
#     chin2y=ry2y[0],
#     chibn2y=ry2y[1],
#     xiny=rh1y[0],
#     xibny=rh1y[1],
# )

# print(an_formula.evalf(subs=values))
# print(bn_formula.evalf(subs=values))

# evaluate for an example



def core_shell_eval_ab(
    n_max, k, r_core, r_shell, n_core, n_shell, n_env=1, mu=1, mu_core=1, mu_shell=1
):
    # todo: vectorize multi-wavenumber k with correct broadcasting
    assert type(n_max) == int
    n = np.arange(1, n_max + 1)

    # - pre-evaluation
    n1 = n_core / n_env
    n2 = n_shell / n_env
    x = k * r_core
    y = k * r_shell

    rj1x = riccati_j_n(n, n1 * x)
    rj2x = riccati_j_n(n, n2 * x)
    rjy = riccati_j_n(n, y)
    rj2y = riccati_j_n(n, n2 * y)

    ry2x = riccati_y_n(n, n2 * x)
    ry2y = riccati_y_n(n, n2 * y)

    rh1y = riccati_h1_n(n, y)

    # - subsitution
    m1 = n1
    m2 = n2
    mu = mu_env
    mu1 = mu_core
    mu2 = mu_shell
    psin1x = rj1x[0]
    psibn1x = rj1x[1]
    psin2x = rj2x[0]
    psibn2x = rj2x[1]
    psiny = rjy[0]
    psibny = rjy[1]
    psin2y = rj2y[0]
    psibn2y = rj2y[1]
    chin2x = ry2x[0]
    chibn2x = ry2x[1]
    chin2y = ry2y[0]
    chibn2y = ry2y[1]
    xiny = rh1y[0]
    xibny = rh1y[1]

    # - eval.
    an = (
        chibn2x * m1 * m2 * mu * mu2 * psibny * psin1x * psin2y
        - chibn2x * m1 * mu2**2 * psibn2y * psin1x * psiny
        + chibn2y * m1 * mu2**2 * psibn2x * psin1x * psiny
        - chibn2y * m2 * mu1 * mu2 * psibn1x * psin2x * psiny
        - chin2x * m2**2 * mu * mu1 * psibn1x * psibny * psin2y
        + chin2x * m2 * mu1 * mu2 * psibn1x * psibn2y * psiny
        - chin2y * m1 * m2 * mu * mu2 * psibn2x * psibny * psin1x
        + chin2y * m2**2 * mu * mu1 * psibn1x * psibny * psin2x
    ) / (
        chibn2x * m1 * m2 * mu * mu2 * psin1x * psin2y * xibny
        - chibn2x * m1 * mu2**2 * psibn2y * psin1x * xiny
        + chibn2y * m1 * mu2**2 * psibn2x * psin1x * xiny
        - chibn2y * m2 * mu1 * mu2 * psibn1x * psin2x * xiny
        - chin2x * m2**2 * mu * mu1 * psibn1x * psin2y * xibny
        + chin2x * m2 * mu1 * mu2 * psibn1x * psibn2y * xiny
        - chin2y * m1 * m2 * mu * mu2 * psibn2x * psin1x * xibny
        + chin2y * m2**2 * mu * mu1 * psibn1x * psin2x * xibny
    )

    bn = (
        chibn2x * m2**2 * mu * mu1 * psibn2y * psin1x * psiny
        - chibn2x * m2 * mu1 * mu2 * psibny * psin1x * psin2y
        + chibn2y * m1 * m2 * mu * mu2 * psibn1x * psin2x * psiny
        - chibn2y * m2**2 * mu * mu1 * psibn2x * psin1x * psiny
        - chin2x * m1 * m2 * mu * mu2 * psibn1x * psibn2y * psiny
        + chin2x * m1 * mu2**2 * psibn1x * psibny * psin2y
        - chin2y * m1 * mu2**2 * psibn1x * psibny * psin2x
        + chin2y * m2 * mu1 * mu2 * psibn2x * psibny * psin1x
    ) / (
        chibn2x * m2**2 * mu * mu1 * psibn2y * psin1x * xiny
        - chibn2x * m2 * mu1 * mu2 * psin1x * psin2y * xibny
        + chibn2y * m1 * m2 * mu * mu2 * psibn1x * psin2x * xiny
        - chibn2y * m2**2 * mu * mu1 * psibn2x * psin1x * xiny
        - chin2x * m1 * m2 * mu * mu2 * psibn1x * psibn2y * xiny
        + chin2x * m1 * mu2**2 * psibn1x * psin2y * xibny
        - chin2y * m1 * mu2**2 * psibn1x * psin2x * xibny
        + chin2y * m2 * mu1 * mu2 * psibn2x * psin1x * xibny
    )
    return an, bn


n_max = 5
k = 2 * np.pi / (wl / n_env)
a, b = core_shell_eval_ab(
    n_max=n_max, k=k, r_core=r_core, r_shell=r_shell, n_core=n_core, n_shell=n_shell
)


prefactor = 2 / (k**2 * r_shell**2)
n = np.arange(1, n_max+1)
qext = prefactor * np.sum((2 * n + 1) * (a.real + b.real))
qsca = prefactor * np.sum((2 * n + 1) * (a.real**2 + a.imag**2 + b.real**2 + b.imag**2))
qabs = qext - qsca


print(qext, qsca, qabs)


# --- compare to existing code
import PyMieScatt as ps

Q_dict = ps.MieQCoreShell(
    mCore=n_core,
    mShell=n_shell,
    wavelength=wl,
    dCore=2 * r_core,
    dShell=2 * r_shell,
    nMedium=n_env,
    asCrossSection=False,
    asDict=True,
)

print(Q_dict["Qext"], Q_dict["Qsca"], Q_dict["Qabs"])


# # compare coefficients to pymiescatt

# ab_pms = ps.CoreShell.CoreShell_ab(mCore=n_core, mShell=n_shell, 
#                          xCore = np.pi*2 * r_core/wl,
#     xShell = np.pi*2 * r_shell/wl)

# print(a)
# print(ab_pms[0][:len(a)])
# print("-------")
# print(b)
# print(ab_pms[1][:len(b)])

