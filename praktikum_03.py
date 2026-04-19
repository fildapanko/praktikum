# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from uncertainties.umath import cos

# nejistoty typu B pro digitalni pristroje
def unc_B_digital(reading, percent_reading, digits, resolution):    # vse musi byt ve spravnych jednotkach; funguje pouze pro jedny podminky zaroven
    '''
    Vypocet nejistoty typu B pro digitalni mereni (ponechame krajni)

    reading : float nebo array
        namerena hodnota
    percent_reading : float
        % of reading
    digits : float
        pocet digitu
    resolution : float
        nejmensi dilek
    '''
    max_error = abs(reading) * (percent_reading/100) + digits * resolution  # max_error -- krajni nejistota
    u_B = max_error / 3

    return u_B

# nejistota typu A 
def unc_A(data):
    """
    Výpočet nejistoty typu A
    data : list nebo array
         měření
    return : float
        nejistota typu A
    """
    data = np.array(data)
    n = len(data)

    s = np.std(data, ddof=1)
    u_A = s / np.sqrt(n)
    
    return u_A

# nejistota typu B u cteni z nejmensiho dilku
def unc_B_cteni(a):
    '''
    Nejistota typu B pro napr pravitko
    a : float
        nejmensi dilek
    return : float
        nejistota typu B
    '''
    u_B = a/(3**0.5)
    return u_B


# mariott
h = uf(10.02, unc_B_cteni(0.01))*(1e-2)
m = uf(43.233, 0.01/3)*(1e-3)
R = uf(0.570, 0.001)*(1e-3)
L = uf(165.0, 0.5)*(1e-3)
cas = uf(181, 1)
g = 9.81275
rho = 997.91

eta = (np.pi*(R**4)*h*(rho**2)*g*cas)/(8*m*L)
print(f'Dynamická viskzita vody je: {eta:.1uPL}')

# pyknometr
mp = uf(24.140, 0.01/3)*(1e-3)
ml = uf(65.071, 0.01/3)*(1e-3)
mv = uf(74.621, 0.01/3)*(1e-3)
rhov = 997.91
rhoair = 1.173356

rholih = ((rhov-rhoair)*((ml-mp)/(mv-mp)))+rhoair
print(f'Hustota lihu je: {rholih:.1uPL}')

# ponor
mlih = uf(4.179, 0.01/3)*(1e-3)
mvoda = uf(5.155, 0.01/3)*(1e-3)
rhovoda = 997.91

rholihponor = (mlih/mvoda)*rhovoda
print(f'Hustota lihu z metody ponoru je: {rholihponor:.1uPL}')

# nacteni google tabulek
sheet_id = '1aA7DkKEpSYSYNvp7ht1wCkUnbj6s1MI4GumqeKJeQNg'
gid = '1873284973'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_povrch = pd.read_csv(url)

# krouzek
f = 0.77
D = uf(58.0, 0.1)*(1e-3)
lih = (np.array(df_povrch['lih']))*(1e-3)
voda = (np.array(df_povrch['voda']))*(1e-3)

Flih = uf(np.mean(lih), unc_A(lih))
Fvoda = uf(np.mean(voda), unc_A(voda))

sigmalih = (Flih/(2*np.pi*D))*f
sigmavoda = (Fvoda/(2*np.pi*D))*f

print(f'Povrchové napětí lihu je: {sigmalih:.1uPL}')
print(f'Povrchové napětí vody je: {sigmavoda:.1uPL}')

# ubbelohde
K = uf(1.063, 1.063*0.0065)
teplota = np.array([22.8, 31.4, 39.2])
rhodest = np.array([997.59, 995.2, 992.51])
casy = np.array([896, 749, 655])

etadest = (1.063*1e-3*casy)/rhodest

teploty = np.linspace(0, 60, 1000) + 273.15
funkce_viskozity = 100/(2.20065*(teploty-282.92341+(8761.27+(teploty-282.92341)**2)**0.5)-129.908)

# graf
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr'$T\,(°C)$', fontsize=20)
ax.set_ylabel(fr'$\eta\,(Pa\,s)$', fontsize=20)
ax.plot(teploty-273.15, funkce_viskozity*1e-3, label='Funkce viskozity', color='blue')
ax.scatter(teplota, etadest, marker='.', label='Vypočítané hodnoty', color='red', s=200)
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r'C:\Users\Admin\Downloads\viskozita.png', dpi=300, bbox_inches='tight')

# kapky
sigmakal = 0.0508
sigmavodatab = 0.07275

thetakal = uf(np.mean(np.array([94.6, 84.4, 84.5])), unc_A(np.array([94.6, 84.4, 84.5])))
thetavoda = uf(np.mean(np.array([107.8, 107.8, 110.8])), unc_A(np.array([107.8, 107.8, 110.8])))

sigmalw = ((sigmavodatab**2)/sigmakal)*(((1+ cos(thetavoda))/(1+ cos(thetakal)))**2)
print(f'Disperzní povrchové napětí vody je: {sigmalw:.1uPL}')