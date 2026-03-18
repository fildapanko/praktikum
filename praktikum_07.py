# import knihoven
import pandas as pd
import numpy as np
from uncertainties import ufloat as uf
from scipy import scipy.optimize


# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "0"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df_tlaky = pd.read_csv(url)


# nejistota typu A 
def uncertainty_typeA(data):
    """
    Výpočet nejistoty typu A

    data : list nebo numpy array
        opakovaná měření
    return : float
        nejistota typu A
    """
    data = np.array(data)
    n = len(data)

    s = np.std(data, ddof=1)  # výběrová směrodatná odchylka
    u_A = s / np.sqrt(n)
    
    return u_A
