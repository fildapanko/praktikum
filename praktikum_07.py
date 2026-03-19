# import knihoven
import pandas as pd
import numpy as np
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from uncertainties import unumpy as unp


# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "0"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df_tlaky = pd.read_csv(url)


# nejistota typu A 
def unc_A(data):
    """
    Výpočet nejistoty typu A
    data : list nebo numpy array
        opakovaná měření
    return : float
        nejistota typu A
    """
    data = np.array(data)
    n = len(data)

    s = np.std(data, ddof=1) 
    u_A = s / np.sqrt(n)
    
    return u_A


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


# nejistota u cteni z nejmensiho dilku
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


# clement desormes metoda
p1 = np.array(df_tlaky['p1'])
p2 = np.array(df_tlaky['p2'])

u_p1 = np.array(unc_B_digital(df_tlaky['p1'], 0.3, 0, 1)) 
u_p2 = np.array(unc_B_digital(df_tlaky['p2'], 0.3, 0, 1))

p0_u = uf(992.7, 0.3)
p1_u = unp.uarray(p1, u_p1)
p2_u = unp.uarray(p2, u_p2)

kappa = p1_u/(p1_u - p2_u)

values = unp.nominal_values(kappa)
errors = unp.std_devs(kappa)

weights = 1 / errors**2
mean = np.sum(weights * values) / np.sum(weights)
u = np.sqrt(1 / np.sum(weights))

kappa_u = uf(mean, u)

print(f'{kappa_u:.1u}')