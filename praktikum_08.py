# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from uncertainties import unumpy as unp
from scipy import stats


# funkce na Studentuv koeficient
def StudCoef(confidence, dof): 
    """
    Parametry
    confidence : float
        hladina spolehlivosti, typicke hodnoty 0.683, 0.9973;
    dof : 
        pocet stupnu volnosti, pro jednoduchou statistiku array.size-1
    Returns : float
    Studentuv koeficient pro danou hladinu spolehlivosti a pocet stupnu volnosti
    """
    alpha = 1 - confidence
    return stats.t.ppf(1 - alpha/2, dof) 


# nejistoty typu B pro digitalni pristroje
def unc_B_digital(reading, percent_reading, digits, resolution):    # vse musi byt ve spravnych jednotkach; funguje pouze pro jedny podminky zaroven
    """
    Vypocet nejistoty typu B pro digitalni mereni (ponechame krajni)

    reading : float nebo array
        namerena hodnota
    percent_reading : float
        % of reading
    digits : float
        pocet digitu
    resolution : float
        nejmensi dilek
    """

    max_error = abs(reading) * (percent_reading/100) + digits * resolution  # max_error -- krajni nejistota
    u_B = max_error / 3

    return u_B


# nacteni google tabulek
sheet_id = "1SabDjWsPIsUqenpKLWSS_sL0DrfNNjyDOQ5PH-PDqho"
gid = "1924903675"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_infra = pd.read_csv(url)


# emisivita povrchu
t = np.array(df_infra['Ccerna'])
tir = np.array(df_infra['cerna'])

unc_t = unc_B_digital(df_infra['Ccerna'], 0.15, 10, 0.1)
unc_tir = unc_B_digital(df_infra['cerna'], 0, 15, 0.1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)

# funkce na vazeny prumer
def weight_average(hodnota): # hodnota : uarray
    values = unp.nominal_values(hodnota)
    errors = unp.std_devs(hodnota)
    weights = 1 / errors**2
    mean = np.sum(weights * values) / np.sum(weights)
    unc = np.sqrt(1 / np.sum(weights))
    unc = unc * StudCoef(0.9973, 4)
    return uf(mean, unc) # return : ufloat

epsilon = weight_average(epsilon)
print(f'Epsilon černé desky je: {epsilon:.1u}')


t = np.array(df_infra['Cseda'])
tir = np.array(df_infra['seda'])

unc_t = unc_B_digital(df_infra['Cseda'], 0.15, 10, 0.1)
unc_tir = unc_B_digital(df_infra['seda'], 0, 15, 0.1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)
epsilon = weight_average(epsilon)
print(f'Epsilon šedé desky je: {epsilon:.1u}')


# propustnost okenek
ir = np.array(df_infra['Ckremik'])
okno = np.array(df_infra['kremik'])

unc_ir = unc_B_digital(df_infra['Ckremik'], 0, 15, 0.1)
unc_okno = unc_B_digital(df_infra['kremik'], 0, 15, 0.1)

ir_unc = unp.uarray(ir, unc_ir)
okno_unc = unp.uarray(okno, unc_okno)

tau = ((okno_unc+273.15)**4)/((ir_unc+273.15)**4)
tau = weight_average(tau)
print(f'Tau křemíku je: {tau:.1u}')


ir = np.array(df_infra['Cnacl'])
okno = np.array(df_infra['nacl'])

unc_ir = unc_B_digital(df_infra['Cnacl'], 0, 15, 0.1)
unc_okno = unc_B_digital(df_infra['nacl'], 0, 15, 0.1)

ir_unc = unp.uarray(ir, unc_ir)
okno_unc = unp.uarray(okno, unc_okno)

tau = ((okno_unc+273.15)**4)/((ir_unc+273.15)**4)
tau = weight_average(tau)
print(f'Tau NaCl je: {tau:.1u}')


# zmrazena ledova deska
t = np.array(df_infra['Cled'])
tir = np.array(df_infra['led'])

unc_t = unc_B_digital(df_infra['Cled'], 0.15, 10, 0.1)
unc_tir = unc_B_digital(df_infra['led'], 0, 15, 0.1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)
epsilon = weight_average(epsilon)
print(f'Epsilon poledované desky je: {epsilon:.1u}')

t = np.array(df_infra['Cmed'])
tir = np.array(df_infra['med'])

unc_t = unc_B_digital(df_infra['Cmed'], 0.15, 10, 0.1)
unc_tir = unc_B_digital(df_infra['med'], 0, 15, 0.1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)
epsilon = weight_average(epsilon)
print(f'Epsilon měděné desky je: {epsilon:.1u}')


# relaxacni doba

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

popt, pcov = curve_fit(model, t, U, p0=p0, maxfev=10000)
A, tau, U_inf = popt
unc_A, unc_tau, unc_Uinf = np.sqrt(np.diag(pcov))
U_fit = np.linspace(min(t), max(t), 1000)

tau_unc = uf(tau, unc_tau)
print(f'Relaxační doba je: {tau_unc:.1u}')

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr"$t\,(s)$", fontsize=20)
ax.set_ylabel(fr"$U\,(V)$", fontsize=20)
ax.plot(df_relax['cas'], df_relax['napeti'], label='Hodnoty', color='blue')
ax.plot(U_fit+df_relax.iloc[555,0], model(U_fit, *popt), label="Exponenciální fit", color='red')
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r"C:\Users\Admin\Downloads\relaxdoba.png", dpi=300)



# olejova lazen

# nacteni google tabulek
sheet_id = "1SabDjWsPIsUqenpKLWSS_sL0DrfNNjyDOQ5PH-PDqho"
gid = "894266709"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_olej = pd.read_csv(url)

# linearni fit
def linear_model(x, a, b):
    return a * x + b

# funkce na fitovani
popt, pcov = curve_fit(linear_model, df_olej['teplota'], df_olej['napeti'],p0=None, bounds=(0, np.inf))
A, b = popt # OPTimalni Parametry -- popt
A_u, b_u = np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice
A = uf(A, A_u)
b = uf(b, b_u)
U_fit = np.linspace(34, 100, 100)
print(f'Závislost prvního čidla je: {A:.1u}')

# graf a fit
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr'$T\,(°C)$', fontsize=20)
ax.set_ylabel(fr'$U\,(V)$', fontsize=20)
ax.scatter(df_olej['teplota'], df_olej['napeti'],marker=".",label='Naměřené hodnoty', color='blue', s=100)
ax.plot(U_fit, linear_model(U_fit, *popt), label=fr"Lineární fit: $\beta$ = {A:.1uPL} $V/°C$", color='cyan')
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r"C:\Users\Admin\Downloads\olejnapeti.png", dpi=300)


# funkce na fitovani
popt, pcov = curve_fit(linear_model, df_olej['teplota'], df_olej['odpor1'],p0=None, bounds=(0, np.inf))
A, b = popt # OPTimalni Parametry -- popt
A_u, b_u = np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice
A = uf(A, A_u)
b = uf(b, b_u)
U_fit = np.linspace(34, 100, 100)
A = A/b
print(f'Závislost druhého čidla je: {A:.1uPL} \n R0 je: {b:.1uPL}')

# graf a fit
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr'$T\,(°C)$', fontsize=20)
ax.set_ylabel(fr'$R\,(\Omega)$', fontsize=20)

ax.scatter(df_olej['teplota'], df_olej['odpor1'],marker=".",label='Naměřené hodnoty', color='red', s=100)
ax.scatter(df_olej['teplota'], df_olej['odpor2'],marker=".",label='Naměřené hodnoty', color='green', s=100)

ax.plot(U_fit, linear_model(U_fit, *popt), label=fr'Lineární fit: $\alpha_1$ = {A:.1uPL} 'r'$\mathrm{°C}^{-1}$', color='orange')

# funkce na fitovani
popt, pcov = curve_fit(linear_model, df_olej['teplota'], df_olej['odpor2'],p0=None, bounds=(0, np.inf))
A, b = popt # OPTimalni Parametry -- popt
A_u, b_u = np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice
A = uf(A, A_u)
b = uf(b, b_u)
U_fit = np.linspace(34, 100, 100)
A = A/b
print(f'Závislost třetího čidla je: {A:.1uPL} \n R0 je: {b:.1uPL}')

ax.plot(U_fit, linear_model(U_fit, *popt), label=fr'Lineární fit: $\alpha_2$ = {A:.1uPL} 'r'$\mathrm{°C}^{-1}$', color='lime')

ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r"C:\Users\Admin\Downloads\olejodpor.png", dpi=300)
