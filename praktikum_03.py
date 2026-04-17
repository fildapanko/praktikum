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
    a : float
        nejmensi dilek
    return : float
        nejistota typu B
    '''
    u_B = a/(3**0.5)
    return u_B

# nacteni google tabulek
sheet_id = '1aA7DkKEpSYSYNvp7ht1wCkUnbj6s1MI4GumqeKJeQNg'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
df_viskozita = pd.read_csv(url)

print(df_viskozita)