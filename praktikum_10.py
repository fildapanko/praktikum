# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from uncertainties import unumpy as unp

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

# nejistota typu B u cteni z nejmensiho dilku
def unc_B_cteni(a):
    '''
    Nejistota typu B pro napr pravitko
    data : float
        nejmensi dilek
    return : float
        nejistota typu B
    '''
    u_B = a/(3**0.5)
    return u_B

# nacteni google tabulek
sheet_id = '1-gAxoP9AR2T-n1tWcYkSS5xTOWZT-rAsQrL7hLmmTmw'
gid = '2066565805'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_vedeni = pd.read_csv(url)

# graf
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr'$t\,(s)$', fontsize=20)
ax.set_ylabel(fr'$U\,(V)$', fontsize=20)
ax.plot(df_vedeni['t'], df_vedeni['a'], label='1. čidlo', color='blue')
ax.plot(df_vedeni['t'], df_vedeni['b'], label='2. čidlo', color='red')
ax.plot(df_vedeni['t'], df_vedeni['c'], label='3. čidlo', color='green')
ax.plot(df_vedeni['t'], df_vedeni['d'], label='4. čidlo', color='orange')
ax.plot(df_vedeni['t'], df_vedeni['e'], label='5. čidlo', color='purple')
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)
ax.legend(fontsize=15)
plt.savefig(r'C:\Users\Admin\Downloads\termoclanky.png', dpi=300, bbox_inches='tight')

# lambda
a = 2.5780594
e = 0.10678545

t1 = uf(63+20.9,2.2/3)
t2 = uf(3+20.9,2.2/3)

l = uf(0.228 - 0.052, unc_B_cteni(0.001))
u = uf(7.019, unc_B_digital(7.019, 0.02, 4, 0.001))
i = uf(0.374, unc_B_digital(0.374, 0.3, 3, 0.001))
d = uf(0.01, unc_B_cteni(0.001))

lambd = (u*i*4*l)/(np.pi*(d**2)*(t1-t2))
print(f'Lambda je: {lambd:.1uPL}')