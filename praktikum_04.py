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
U_fit1 = np.linspace(min(df_kyvadlo['z1']), max(df_kyvadlo['z1']), 200)

popt2, err2 = fit_poly(df_kyvadlo['z2'], df_kyvadlo['T2'])
a02, b02, c02 = popt2
a_u, b_u, c_u = err2
a2 = uf(a02, a_u)
b2 = uf(b02, b_u)
c2 = uf(c02, c_u)
U_fit2 = np.linspace(min(df_kyvadlo['z2']), max(df_kyvadlo['z2']), 200)


# graf a fit
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr'$z\,(mm)$', fontsize=20)
ax.set_ylabel(fr'$t\,(s)$', fontsize=20)
ax.scatter(df_kyvadlo['z1'], df_kyvadlo['T1'],marker='.',label='Naměřené hodnoty', color='blue', s=100)
ax.plot(U_fit1, polynom_model(U_fit1, *popt1), label=fr'Fit polynomem ($ax^2+bx+c$)', color='cyan')


ax.scatter(df_kyvadlo['z2'], df_kyvadlo['T2'],marker='.',label='Naměřené hodnoty', color='red', s=100)
ax.plot(U_fit2, polynom_model(U_fit2, *popt2), label=fr'Fit polynomem ($ax^2+bx+c$)', color='orange')

# rozdilovy polynom
coeffs = [a01 - a02, b01 - b02, c01 - c02]
roots = np.roots(coeffs)
intersections = [
    (r.real, a01*r.real**2 + b01*r.real + c01)
    for r in roots
    if np.isreal(r) and r.real > 0
]
# vykresleni pruseciku
for x, y in intersections:
    plt.scatter(x, y, marker='x',label='Průsečík', color='green', s=200)
    plt.annotate(
    f'({x:.3f}, {y:.3f})',
    (x, y),
    xytext=(8, -15),
    textcoords='offset points',
)

ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r'C:\Users\Admin\Downloads\kyvadlo.png', dpi=300, bbox_inches='tight')