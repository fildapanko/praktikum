# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit

# nacteni google tabulek
sheet_id = '1h2iV1PbB3VpKC6OpQwYhCfeMAKmC3iLTg9_OAIoH-6E'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_kap = pd.read_csv(url)


studena_k = df_kap.loc[0,'studena']
kalorimetr = df_kap.loc[0,'kalorimetr']
studena = uf(studena_k - kalorimetr, 0.1)*1e-3
print(f'Hmotnost studené vody je: {studena:.2uPL}')

tepla_n = df_kap.loc[0,'tepla']
nadoba = df_kap.loc[0,'nadoba']
tepla = uf(tepla_n - nadoba, 0.1)*1e-3
print(f'Hmotnost teplé vody je: {tepla:.2uPL}')

ts = uf(df_kap.loc[0,'ts'], 0.1)
tt = uf(df_kap.loc[0,'tt'], 0.1)
t = uf(df_kap.loc[0,'t'], 0.1)

kappa = tepla*((tt-t)/(t-ts))-studena
print(f'Redukovaná kapacita je: {kappa:.2uPL}')

# nacteni google tabulek
sheet_id = '1h2iV1PbB3VpKC6OpQwYhCfeMAKmC3iLTg9_OAIoH-6E'
gid = '175470021'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_vykon = pd.read_csv(url)

p = df_vykon.loc[0,'p']
tr = uf(df_vykon.loc[0,'tr'], 0.1)
to = uf(df_vykon.loc[0,'to'], 0.1)
beta = (p)/(tr-to)
print(f'Koeficient chladnutí je: {beta:.2uPL}')


# nacteni google tabulek
sheet_id = '1h2iV1PbB3VpKC6OpQwYhCfeMAKmC3iLTg9_OAIoH-6E'
gid = '1678285414'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_data = pd.read_csv(url)

# graf a fit
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr'$\tau\,(s)$', fontsize=20)
ax.set_ylabel(fr'$t\,(°C)$', fontsize=20)
ax.plot(df_data['cas'], df_data['tep1'],label='Naměřené hodnoty', color='blue')
#ax.plot(U_fit, linear_model(U_fit, *popt), label=fr"Lineární fit: $\beta$ = {A:.1uPL} $V/°C$", color='cyan')
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r"C:\Users\Admin\Downloads\kalorimetr.png", dpi=300)



t1_celk = df_data['tep1']
t1 = t1_celk[1455:]
m = (studena+tepla)
kappa = kappa.n
to = to.n
tau_celk = df_data['cas']
tau = tau_celk[1455:]


tau = tau_celk[1455:].to_numpy()
tau = tau - tau[0]

# model
def exp_model(x, y0, A, T ):
    return y0 + A * np.exp((-x)*T)



popt, pcov = curve_fit(exp_model, tau, t1, maxfev = 10000)
_, _, T = popt
_, _, unc_T = np.sqrt(np.diag(pcov))
T = uf(T, unc_T)
gamma = T*(m+kappa)
print(f'Redukovaný koeficient je: {gamma:.2uPL}')

t_fit = np.linspace(min(tau), max(tau), 1000)


fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr"$\tau\,(s)$", fontsize=20)
ax.set_ylabel(fr"$t\,(°C)$", fontsize=20)
ax.plot(tau, t1, label='Hodnoty', color='blue')
ax.plot(t_fit, exp_model(t_fit, *popt), label="Exponenciální fit", color='red')
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r"C:\Users\Admin\Downloads\chladnuti.png", dpi=300)