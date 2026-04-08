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
    '''
    Parametry
    confidence : float
        hladina spolehlivosti, typicke hodnoty 0.683, 0.9973;
    dof : 
        pocet stupnu volnosti, pro jednoduchou statistiku array.size-1
    Returns : float
    Studentuv koeficient pro danou hladinu spolehlivosti a pocet stupnu volnosti
    '''
    alpha = 1 - confidence
    return stats.t.ppf(1 - alpha/2, dof)

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

# nacteni google tabulek
sheet_id = '1fWm_pEDu0Hblxh12eK3tPYXtQ9wCVlQNpoaQT7EcBMM'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_analog = pd.read_csv(url)


# analogova cast

# vnitrni odpor ampermetru
I = df_analog.loc[0, 'ia']
unc_I = 1.5e-6
I_unc = uf(I*1e-6, unc_I)

U = df_analog.loc[0, 'uv']
unc_U = unc_B_digital(U, 0.02, 4, 1e-4)
U_unc = uf(U, unc_U)

R = U_unc/I_unc
print(f'Vnitřní odpor ampérmetru přímo z Ohmova zákona je: {R:.1uPL}')
print('Vnitřní odpor ampérmetru ze substituční metody je: 1580 +- ??')

# bocniky
print('Velikosti bočníků jsou: 400, 180, 85')

# predradniky
print('Velikosti předřadníků jsou: 49000 a 99500')


# digitalni cast

# nacteni google tabulek
sheet_id = '1fWm_pEDu0Hblxh12eK3tPYXtQ9wCVlQNpoaQT7EcBMM'
gid = '1500912534'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_digital = pd.read_csv(url)

# realny napetovy rozsah
Ur12 = df_digital.loc[0,'um12'] - df_digital.loc[0,'u012']
Uq12 = Ur12 /(2**12 - 1)
print(f'Reálný rozsah 12-ti bitového převodníku je: {Ur12}')
print(f'Reálný kvantizační krok 12-ti bitového převodníku je: {Uq12}')
Ur16 = df_digital.loc[0,'um16'] - df_digital.loc[0,'u016']
Uq16 = (2*Ur16)/(2**16 - 1)
print(f'Reálný rozsah 16-ti bitového převodníku je: {Ur16}')
print(f'Reálný kvantizační krok 16-ti bitového převodníku je: {Uq16}')

# chyba offsetu a měřítka
deltaU0 = df_digital.loc[0,'u012'] - (1/(2**12 - 1))
deltaUm = df_digital.loc[0,'um12'] - 5

delta0 = deltaU0 / Ur12
deltam = (deltaUm - delta0) / Ur12

print(f'Chyba offsetu je: {delta0}')
print(f'Chyba měřítka je: {deltam}')