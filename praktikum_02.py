# import knihoven
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from uncertainties.umath import *
from uncertainties import unumpy as unp
from scipy import stats
from scipy.optimize import curve_fit


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
def u_B_digital(reading, percent_reading, digits, resolution):    # vse musi byt ve spravnych jednotkach; funguje pouze pro jedny podminky zaroven
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
    u_B = max_error

    return u_B

# nacteni hodnot z google tabulek
sheet_id = "1QG5bClfVFrBsCKqHhvaXQRN1fuG5CaGDWVyeGqLaWt0"   # tabulka
gid = "1250966535"  # list
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_odpor = pd.read_csv(url) # data frame


# Metoda A
# R1
U1A = uf(df_odpor.loc[0, "Uv"], u_B_digital(df_odpor.loc[0, "Uv"], 0.02, 4, 1e-4))  # V
I1A = uf(df_odpor.loc[0, "Ia"], u_B_digital(df_odpor.loc[0, "Ia"], 0.2, 3, 1e-5))   # A
R_v = 11.1e6 # ohm

R_1Aa = U1A/I1A
R_1Ab = U1A/(I1A - (U1A/R_v))

#  R2
U2A = uf(df_odpor.loc[2, "Uv"], u_B_digital(df_odpor.loc[2, "Uv"], 0.02, 4, 1e-4))  # V
I2A = uf(df_odpor.loc[2, "Ia"], u_B_digital(df_odpor.loc[2, "Ia"], 0.2, 3, 1e-7))   # A
R_v = 11.1e6 # ohm

R_2Aa = U2A/I2A
R_2Ab = U2A/(I2A - (U2A/R_v))


# Metoda B
# R1
U1B = uf(df_odpor.loc[1, "Uv"], u_B_digital(df_odpor.loc[1, "Uv"], 0.02, 4, 1e-4))  # V
I1B = uf(df_odpor.loc[1, "Ia"], u_B_digital(df_odpor.loc[1, "Ia"], 0.2, 3, 1e-5))   # A
R_a = 1 # ohm

R_1Ba = U1B/I1B
R_1Bb = (U1B/I1B) - R_a

#  R2
U2B = uf(df_odpor.loc[3, "Uv"], u_B_digital(df_odpor.loc[3, "Uv"], 0.02, 4, 1e-4))  # V
I2B = uf(df_odpor.loc[3, "Ia"], u_B_digital(df_odpor.loc[3, "Ia"], 0.2, 3, 1e-7))   # A
R_a = 1 # ohm

R_2Ba = U2B/I2B
R_2Bb = (U2B/I2B) - R_a




# nacteni hodnot z google tabulek
sheet_id = "1QG5bClfVFrBsCKqHhvaXQRN1fuG5CaGDWVyeGqLaWt0"
gid = "0"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_voltamper = pd.read_csv(url)


# linearni fit
def linear_model(x, a, b):
    return a * x + b

# fit polynomem
def polynom_model(x, a, b, c):
    return a*x**2 + b*x + c

# odhad parametru, hranice
R_initial = df_voltamper.loc[0,"Uv"] / (df_voltamper.loc[0, "Ia"]/1000)
b_initial = 0
p0 = [R_initial, b_initial]

bounds = (0, np.inf)


# vypocet hodnot pro fit
popt, pcov = curve_fit(linear_model, df_voltamper["Uv"], df_voltamper["Ia"], p0=p0, bounds=bounds)

R, b = popt # OPTimalni Parametry -- popt
R_u, b_u = np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice

R_unc = uf(R, R_u)
b_unc = uf(b, b_u)

R_konec = 1/(R_unc * 1e-3)

# graf hodnot
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlabel(fr"$U~[V]$", fontsize=20)
ax.set_ylabel(fr"$I~[mA]$", fontsize=20)
ax.scatter(df_voltamper["Uv"], df_voltamper["Ia"],marker=".",label="Naměřené hodnoty", color="blue", s=250)
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)


# vykresleni fitu
U_fit = np.linspace(df_voltamper["Uv"].min(), df_voltamper["Uv"].max(), 100)

ax.plot(U_fit, linear_model(U_fit, *popt), label=f"Lineární fit (Ax + b):\n$A$ = {R}\n$b$ = {b}", color="red")

# vypocet hodnot pro fit polynomem
popt, pcov = curve_fit(polynom_model, df_voltamper["Uv"], df_voltamper["Ia"], p0=None, bounds=(-np.inf, np.inf))

a, b, c = popt # OPTimalni Parametry -- popt
a_u, b_u , c_u= np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice

ax.plot(U_fit, polynom_model(U_fit, *popt), label=f'Fit polynomem (ax$^2$ + bx + c):\n$a$ = {a}\n$b$ = {b}\n$c$ = {c}', color="lime")

ax.legend(fontsize=15)
plt.savefig(r"C:\Users\Admin\Downloads\VAchar.png", dpi=300, bbox_inches='tight')
print(f'Výsledný odpor z lineárního fitu je: {R_konec}')

print(f"odpory jsou: \n Metoda A: \n {R_1Aa:.1u} \n {R_1Ab:.1u} \n {R_2Aa:.1u} \n {R_2Ab:.1u} \n Metoda B: \n {R_1Ba:.1u} \n {R_1Bb:.1u} \n {R_2Ba:.1u} \n {R_2Bb:.1u}")