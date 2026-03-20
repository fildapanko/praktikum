# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from uncertainties import unumpy as unp
from scipy import stats


# rychlost zvuku ve vzduchu


# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "2065785545"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df_zvuk = pd.read_csv(url)


# linearni fit
def linear_model(x, a, b):
    return a * x + b


# odhad parametru, hranice
R_initial = abs(df_zvuk.loc[0,"f840"] - df_zvuk.loc[1,"f840"])
b_initial = 0
p0 = [R_initial, b_initial]
bounds = (0, np.inf)


col = df_zvuk["f840"].dropna()


# vypocet hodnot pro fit
popt, pcov = curve_fit(linear_model, df_zvuk.index[:len(col)].to_numpy(dtype=float), col,p0=None, bounds=(-np.inf, np.inf) )
R, b = popt # OPTimalni Parametry -- popt
R_u, b_u = np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice
R = uf(R, R_u)
b = uf(b, b_u)


# graf hodnot
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_title("lambda pul", fontsize=25, pad=15)
ax.set_xlabel(fr"$i$", fontsize=20)
ax.set_ylabel(fr"$D$", fontsize=20)
ax.scatter(df_zvuk.index, df_zvuk["f840"],marker="o",label="Naměřené hodnoty", color="blue", s=100)
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)


# vykresleni fitu
U_fit = np.linspace(0, 3, 100)

ax.plot(U_fit, linear_model(U_fit, *popt), label=fr"Lineární fit: $R$ = {R:.1uPL} $\Omega$", color="red")

ax.legend(fontsize=15)
plt.show()
