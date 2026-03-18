# import knihoven
import pandas as pd
import numpy as np
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit


# nacteni google tabulek
sheet_id = "SPREADSHEET_ID"
gid = "0"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df = pd.read_csv(url)


# nejistota typu A 
def uncertainty_typeA(data):
    """
    Výpočet nejistoty typu A (standard uncertainty of the mean)

    data : list nebo numpy array
        opakovaná měření

    return : float
        nejistota typu A
    """
    
    data = np.array(data)
    n = len(data)
    
    if n < 2:
        raise ValueError("Je potřeba alespoň 2 měření")

    s = np.std(data, ddof=1)  # výběrová směrodatná odchylka
    u_A = s / np.sqrt(n)
    
    return u_A



# nejistota typu B pro digitalni pristroje
def uncertainty_typeB_digital(reading, percent_reading, digits, resolution):
    """
    Výpočet standardní nejistoty typu B pro digitální měření.

    reading : float nebo array
        naměřená hodnota
    percent_reading : float
        procentní přesnost (% of reading)
    digits : float
        počet digitů ve specifikaci
    resolution : float
        hodnota jednoho digit (např. 0.01)

    return : float nebo numpy array
        standardní nejistota typu B
    """

    max_error = abs(reading) * percent_reading / 100 + digits * resolution
    u_B = max_error / np.sqrt(3)

    return u_B