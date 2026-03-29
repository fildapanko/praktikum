# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from uncertainties import unumpy as unp
from scipy import stats

# relaxacni doba

# nacteni google tabulek
sheet_id = "1SabDjWsPIsUqenpKLWSS_sL0DrfNNjyDOQ5PH-PDqho"
gid = "408060846"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_relax = pd.read_csv(url)

t = df_relax["cas"].iloc[555:]
U = df_relax["odpor"].iloc[555:]

# normalizace času
t = t - t.min()

# model
def model(t, A, tau, U_inf):
    return U_inf + A * np.exp(-t / tau)

# odhad
p0 = [max(U) - min(U), 10, min(U)]

popt, pcov = curve_fit(model, t, U, p0=p0, maxfev=10000)
A, tau, U_inf = popt
unc_A, unc_tau, unc_Uinf = np.sqrt(np.diag(pcov))
U_fit = np.linspace(min(t), max(t), 1000)

tau_unc = uf(tau, unc_tau)
print(f'Relaxační doba je: {tau_unc:.1u}')

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr"$t\,(s)$", fontsize=20)
ax.set_ylabel(fr"$U\,(V)$", fontsize=20)
ax.plot(df_relax['cas'], df_relax['odpor'], label='Hodnoty', color='blue')
ax.plot(U_fit+df_relax.iloc[555,0], model(U_fit, *popt), label="Exponenciální fit", color='red')
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
#plt.savefig(r"C:\Users\Admin\Downloads\relaxdalsiverze.png", dpi=300)