# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from scipy import stats

# nejistota typu A 
def unc_A(data):
    """
    Výpočet nejistoty typu A
    data : list nebo numpy array
         měření
    return : float
        nejistota typu A
    """
    data = np.array(data)
    n = len(data)

    s = np.std(data, ddof=1)
    u_A = s / np.sqrt(n)
    
    return u_A

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

# rozsirena nejistota
def kraj_unc(ufl):
    nom = ufl.nominal_value
    std = ufl.std_dev
    std_roz = std*StudCoef(0.9973, 9)
    ufr = uf(nom, std_roz)
    return ufr

# drat

# nejistota typu B u cteni z nejmensiho dilku
def unc_B_cteni(a):
    """
    Nejistota typu B pro napr pravitko
    data : float
        nejmensi dilek
    return : float
        nejistota typu B
    """
    u_B = a/(3**0.5)
    return u_B

# kombinovana nejistota -- C
def unc_C(A, B):
    C = (A**2 + B**2)**0.5
    return C

# nacteni google tabulek
sheet_id = '1sf00DWCZsCnZAw545SVOeST13HPtHGi5x8IWbbzFZ4o'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_drat = pd.read_csv(url)

prumer = df_drat['drat']*1e-3
delka = 1567*1e-3
g = 9.81

prumer_Ua = unc_A(prumer)
prumer_Ub = unc_B_cteni(1e-5)
prumer_U = unc_C(prumer_Ua, prumer_Ub)

prumer = uf(np.mean(prumer), prumer_U)

l_dolu = df_drat['dolu']
l_nahoru = df_drat['nahoru']

# linearni funkce
def lin_model(x, a, b):
    return a*x + b

# funkce na fitovani
def fit_lin_unc(x, y):
    popt, pcov = curve_fit(lin_model, x, y)
    err = np.sqrt(np.diag(pcov))
    a, b = popt
    a_u, b_u = err
    a = uf(a, a_u)
    b = uf(b, b_u)
    lnspace = np.linspace(min(x), max(x), 200)
    return a, b, popt, lnspace

# postupny soucet zavazi
zavazi = df_drat['zavazi']
m = []
soucet = 0
for x in zavazi:
    soucet += x
    m.append(soucet)

a1, _, popt1, lnspace1 = fit_lin_unc(m, l_dolu)
a2, _, popt2, lnspace2 = fit_lin_unc(m[::-1], l_nahoru[::-1])

# graf a fit
fig, ax = plt.subplots(1, 2, figsize=(16, 9), sharey=True)
# odstranění mezery
fig.subplots_adjust(wspace=0)
ax[0].scatter(m, l_dolu, marker='.', s=100, label='Naměřené hodnoty – přidávání závaží', color='blue')
ax[1].scatter(m[::-1], l_nahoru[::-1], marker='.', s=100, label='Naměřené hodnoty – oddělávání závaží', color='red')
ax[0].plot(lnspace1, lin_model(lnspace1, *popt1), label=f'Lineární fit: k = {a1:.1uPL}', color='cyan')
ax[1].plot(lnspace2, lin_model(lnspace2, *popt2), label=f'Lineární fit: k = {a2:.1uPL}', color='orange')

ax[0].set_xlabel(r'$m\,(g)$', fontsize=20)
ax[0].set_ylabel(r'$\Delta l\,(mm)$', fontsize=20)
ax[0].grid(True, alpha=0.7)
ax[0].legend(fontsize=15)
ax[0].tick_params(labelsize=15)

ax[1].invert_xaxis()
ax[1].set_xlabel(r'$m\,(g)$', fontsize=20)
ax[1].grid(True, alpha=0.7)
ax[1].legend(fontsize=15)
ax[1].tick_params(labelsize=15)
plt.savefig(r'C:\Users\Admin\Downloads\drat.png', dpi=300, bbox_inches='tight')

koeficient = a1
modul_drat = (4*g*delka)/(np.pi*prumer**2 *koeficient)
modul_drat = kraj_unc(modul_drat)
print(f'Modul pružnosti v tahu drátu je: {modul_drat:.1uPL}')

# desky

# nacteni google tabulek
sheet_id = '1sf00DWCZsCnZAw545SVOeST13HPtHGi5x8IWbbzFZ4o'
gid = '1251551756'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_desky = pd.read_csv(url)

l = df_desky['delka']*1e-2
l = uf(np.mean(l), (unc_C(unc_A(l), unc_B_cteni(1e-3))))

a_d = df_desky['tlust_d']*1e-3
a_d = uf(np.mean(a_d), unc_C(unc_A(a_d),unc_B_cteni(1e-5)))
b_d = df_desky['sirka_d']*1e-2
b_d = uf(np.mean(b_d), unc_C(unc_A(b_d),unc_B_cteni(1e-4)))

a_z = df_desky['tlust_z']*1e-3
a_z = uf(np.mean(a_z), unc_C(unc_A(a_z),unc_B_cteni(1e-5)))
b_z = df_desky['sirka_z']*1e-2
b_z = uf(np.mean(b_z), unc_C(unc_A(b_z),unc_B_cteni(1e-4)))

a_m = df_desky['tlust_m']*1e-3
a_m = uf(np.mean(a_m), unc_C(unc_A(a_m),unc_B_cteni(1e-5)))
b_m = df_desky['sirka_m']*1e-2
b_m = uf(np.mean(b_m), unc_C(unc_A(b_m),unc_B_cteni(1e-4)))


# postupny soucet zavazi
zavazi = df_desky['zavazi (g)']
m = []
soucet = 0
for x in zavazi:
    soucet += x
    m.append(soucet)

dolu_d = df_desky['dolu_d']
nahoru_d = df_desky['nahoru_d']
dolu_z = df_desky['dolu_z']
nahoru_z = df_desky['nahoru_z']
dolu_m = df_desky['dolu_m']
nahoru_m = df_desky['nahoru_m']

a1_d, b1_d, popt1_d, lnspace1_d = fit_lin_unc(m, dolu_d)
a1_z, b1_z, popt1_z, lnspace1_z = fit_lin_unc(m, dolu_z)
a1_m, b1_m, popt1_m, lnspace1_m = fit_lin_unc(m, dolu_m)
a2_d, b2_d, popt2_d, lnspace2_d = fit_lin_unc(m, nahoru_d)
a2_z, b2_z, popt2_z, lnspace2_z = fit_lin_unc(m, nahoru_z)
a2_m, b2_m, popt2_m, lnspace2_m = fit_lin_unc(m, nahoru_m)


fig, ax = plt.subplots(2, 3, figsize=(16, 9), sharex='col', sharey='row')

# nastavení mezer
fig.subplots_adjust(hspace=0,  wspace=0.1) # spojení vertikálně # mezera mezi sloupci

ax[0,0].set_title("Deska 1", fontsize=20, pad=10)
ax[0,0].scatter(m, dolu_d, marker='.', s=100, label='Naměřené hodnoty – přidávání závaží', color='blue')
ax[0,0].plot(lnspace1_d, lin_model(lnspace1_d, *popt1_d), label=f'Lineární fit: k = {a1_d:.1uPL}', color='cyan')
ax[1,0].scatter(m, nahoru_d, marker='.', s=100, label='Naměřené hodnoty – oddělávání závaží', color='red')
ax[1,0].plot(lnspace2_d, lin_model(lnspace2_d, *popt2_d), label=f'Lineární fit: k = {a2_d:.1uPL}', color='orange')

ax[1,0].set_xlabel(r'$m\,(g)$', fontsize=15)
ax[0,0].set_ylabel(r'$\Delta l\,(mm)$', fontsize=15)
ax[1,0].set_ylabel(r'$\Delta l\,(mm)$', fontsize=15)

ax[0,1].set_title("Deska 2", fontsize=20, pad=10)
ax[0,1].scatter(m, dolu_z, marker='.', s=100, label='Naměřené hodnoty – přidávání závaží', color='blue')
ax[0,1].plot(lnspace1_z, lin_model(lnspace1_z, *popt1_z), label=f'Lineární fit: k = {a1_z:.1uPL}', color='cyan')
ax[1,1].scatter(m, nahoru_z, marker='.', s=100, label='Naměřené hodnoty – oddělávání závaží', color='red')
ax[1,1].plot(lnspace2_z, lin_model(lnspace2_z, *popt2_z), label=f'Lineární fit: k = {a2_z:.1uPL}', color='orange')
ax[1,1].set_xlabel(r'$m\,(g)$', fontsize=15)

ax[0,2].set_title("Deska 3", fontsize=20, pad=10)
ax[0,2].scatter(m, dolu_m, marker='.', s=100, label='Naměřené hodnoty – přidávání závaží', color='blue')
ax[0,2].plot(lnspace1_m, lin_model(lnspace1_m, *popt1_m), label=f'Lineární fit: k = {a1_m:.1uPL}', color='cyan')
ax[1,2].scatter(m, nahoru_m, marker='.', s=100, label='Naměřené hodnoty – oddělávání závaží', color='red')
ax[1,2].plot(lnspace2_m, lin_model(lnspace2_m, *popt2_m), label=f'Lineární fit: k = {a2_m:.1uPL}', color='orange')
ax[1,2].set_xlabel(r'$m\,(g)$', fontsize=15)

for ax in ax.flat:
    ax.tick_params(labelbottom=True, labelleft=True)
    ax.grid(True, alpha=0.7)
    ax.legend(fontsize=10, loc='upper left')

plt.savefig(r'C:\Users\Admin\Downloads\desky.png', dpi=300, bbox_inches='tight')

# vypocet
def modul_nosnik(a, b, koef):
    modul_desk = (g * l**3)/(4 * koef * a**3 * b)
    return modul_desk

modul_desk_d  = modul_nosnik(a_d, b_d, a1_d)
modul_desk_z  = modul_nosnik(a_z, b_z, a1_z)
modul_desk_m  = modul_nosnik(a_m, b_m, a1_m)

modul_desk_d = kraj_unc(modul_desk_d)
modul_desk_z = kraj_unc(modul_desk_z)
modul_desk_m = kraj_unc(modul_desk_m)

print(f'Moduly pružnosti v tahu pro nosníky jsou:\nDural = {modul_desk_d:.1uPL}\nMosaz = {modul_desk_z:.1uPL}\nMěď = {modul_desk_m:.1uPL}')

# smyk

# nacteni google tabulek
sheet_id = '1sf00DWCZsCnZAw545SVOeST13HPtHGi5x8IWbbzFZ4o'
gid = '555689286'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_smyk = pd.read_csv(url)

mass = 5.884
T = df_smyk['10 period (s)']/10
l = df_smyk['delka (cm)']*1e-2
D = df_smyk['koule (cm)']*1e-2
d = df_smyk['drat (mm)']*1e-3

T = uf(np.mean(T), (0.05**2 + unc_A(T)**2)**0.5)
l = uf(np.mean(l), (unc_B_cteni(1e-3)**2 + unc_A(l)**2)**0.5)
D = uf(np.mean(D), (unc_B_cteni(1e-4)**2 + unc_A(D)**2)**0.5)
d = uf(np.mean(d), (unc_A(d)**2 + unc_B_cteni(1e-5)**2)**0.5)


modul_koule = (64 * np.pi * mass * D**2 * l)/(5 * d**4 * T**2)
modul_koule = kraj_unc(modul_koule)
print(f'Modul pružnosti ve smyku je: {modul_koule:.1uPL}')

# prendat prumer dratu jinam z tabulky

