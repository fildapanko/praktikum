# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit

# nacteni google tabulek
sheet_id = '10z04lpi1SJIW4qjCqTtfem1v3yCMArCQSHEY15_5Krw'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_kyvadlo = pd.read_csv(url)

# fit polynomem
def polynom_model(x, a, b, c):
    return a*x**2 + b*x + c

# funkce na fitovani
def fit_poly(x, y):
    popt, pcov = curve_fit(polynom_model, x, y)
    err = np.sqrt(np.diag(pcov))
    return popt, err

popt1, err1 = fit_poly(df_kyvadlo['z1'], df_kyvadlo['T1'])
a01, b01, c01 = popt1
a_u, b_u, c_u = err1
a1 = uf(a01, a_u)
b1 = uf(b01, b_u)
c1 = uf(c01, c_u)
z_fit1 = np.linspace(min(df_kyvadlo['z1']), max(df_kyvadlo['z1']), 200)

popt2, err2 = fit_poly(df_kyvadlo['z2'], df_kyvadlo['T2'])
a02, b02, c02 = popt2
a_u, b_u, c_u = err2
a2 = uf(a02, a_u)
b2 = uf(b02, b_u)
c2 = uf(c02, c_u)
z_fit2 = np.linspace(min(df_kyvadlo['z2']), max(df_kyvadlo['z2']), 200)

def intersection(p1, p2):
    coeffs = np.array(p1) - np.array(p2)
    roots = np.roots(coeffs)

    res = []
    for r in roots:
        if np.isreal(r) and r.real > 0:
            x = r.real
            y = np.polyval(p1, x)
            res.append((x, y))
    return res

intersections = intersection(popt1, popt2)

# graf a fit
fig, ax = plt.subplots(figsize=(16, 9))
ax.scatter(df_kyvadlo['z1'], df_kyvadlo['T1'], marker='.', s=100, label='Naměřené hodnoty $T_1$', color='blue')
ax.scatter(df_kyvadlo['z2'], df_kyvadlo['T2'], marker='.', s=100, label='Naměřené hodnoty $T_2$', color='red')
ax.plot(z_fit1, polynom_model(z_fit1, *popt1), label='Fit polynomem ($ax^2+bx+c$)', color='cyan')
ax.plot(z_fit2, polynom_model(z_fit2, *popt2), label='Fit polynomem ($ax^2+bx+c$)', color='orange')

for x, y in intersections:
    ax.scatter(x, y, marker='x', color='green', s=200, label='Průsečík')
    ax.annotate(
        f"({x:.3f}, {y:.3f})",
        (x, y),
        xytext=(8, -15),
        textcoords='offset points'
    )

ax.set_xlabel(r'$z\,(mm)$', fontsize=20)
ax.set_ylabel(r'$t\,(s)$', fontsize=20)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
ax.tick_params(labelsize=15)

plt.savefig(r'C:\Users\Admin\Downloads\kyvadlo.png', dpi=300, bbox_inches='tight')

A = a1 - a2
B = b1 - b2
C = c1 - c2

D = B**2 - 4*A*C

x1 = (-B + D**0.5) / (2*A)
x2 = (-B - D**0.5) / (2*A)

T0 = a1*x1**2 + b1*x1 + c1

delka = uf(98.9*1e-2, 0.0001)

g = (4*np.pi**2 * delka)/(T0**2)
print(f'Graviační zrychlení je: {g:.2uPL}')

# cavendish

# nacteni dat
df_jedna = pd.read_csv(
    "cavendish_machacek_jedna.txt",
    sep="\s+",
    header=None
)
df_jedna.columns = ["t", "x"]

df_dva = pd.read_csv(
    "cavendish_machacek_dva.txt",
    sep="\s+",
    header=None
)
df_dva.columns = ["t", "x"]

t1 = df_jedna['t']
x1 = df_jedna['x']

t2 = df_dva['t']
x2 = df_dva['x']

# graf
fig, ax = plt.subplots(figsize=(16, 9))
ax.scatter((t1-1)/30, x1, marker='.', s=100, label='', color='blue')
ax.scatter((t2-1)/30, x2, marker='.', s=100, label='', color='red')

ax.set_xlabel(r'$t\,(s)$', fontsize=20)
ax.set_ylabel(r'$x\,(pixel)$', fontsize=20)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
ax.tick_params(labelsize=15)

plt.savefig(r'C:\Users\Admin\Downloads\lasernamereno.png', dpi=300, bbox_inches='tight')

# fit
def damped_osc(t, A, gamma, omega, phi, x0):
    return A * np.exp(-gamma * t) * np.cos(omega * t + phi) + x0

A0 = (max(x1) - min(x1)) / 2
y0_0 = np.mean(x1)
gamma0 = 1e-4
omega0 = 2*np.pi / (t1[10] - t1[0])  # hrubý odhad
phi0 = 0

p0 = [A0, gamma0, omega0, phi0, y0_0]

popt, pcov = curve_fit(damped_osc, t1, x1, p0=p0)
A, gamma, omega, phi, x0 = popt

t_fit = np.linspace(min(t1), max(t1), 1000)

fig, ax = plt.subplots(figsize=(16, 9))
ax.scatter(t1, x1, s=10, label="data")
ax.plot(t_fit, damped_osc(t_fit, *popt), color="red", label="fit")
ax.axhline(x0, linestyle='--', color='black', label='rovnovážná poloha')

ax.legend()
ax.grid()
plt.savefig(r'C:\Users\Admin\Downloads\laserfit.png', dpi=300, bbox_inches='tight')