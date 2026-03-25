import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
import numpy as np

# nacteni google tabulek
sheet_id = "1SabDjWsPIsUqenpKLWSS_sL0DrfNNjyDOQ5PH-PDqho"
gid = "408060846"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_relax = pd.read_csv(url)





t = df_relax["cas"].iloc[555:]
U = df_relax["napeti"].iloc[555:]

# normalizace času
t = t - t.min()

# model
def model(t, A, tau, U_inf):
    return U_inf + A * np.exp(-t / tau)

# odhad
p0 = [max(U) - min(U), 10, min(U)]

popt, _ = curve_fit(model, t, U, p0=p0, maxfev=10000)

A, tau, U_inf = popt

print("tau =", tau)
print(U_inf)

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_title("Relaxační doba čidla", fontsize=25, pad=15)
ax.set_xlabel(fr"$t\,(s)$", fontsize=20)
ax.set_ylabel(fr"$U\,(V)$", fontsize=20)
ax.plot(df_relax['cas'], df_relax['napeti'], label='hodnoty', color='blue')
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)

U_fit = np.linspace(min(t), max(t), 1000)
ax.plot(U_fit+df_relax.iloc[555,0], model(U_fit, *popt), label="Exponenciální fit: xxx = ", color='red')
plt.show()
