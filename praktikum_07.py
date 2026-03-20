# import knihoven
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uncertainties import ufloat as uf
from scipy.optimize import curve_fit
from uncertainties import unumpy as unp
from scipy import stats


# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "0"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df_tlaky = pd.read_csv(url)


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
# tlakomer
p1 = np.array(df_tlaky['p1'])
p2 = np.array(df_tlaky['p2'])

u_p1 = np.array(unc_B_digital(df_tlaky['p1'], 0.3, 0, 1)) 
u_p2 = np.array(unc_B_digital(df_tlaky['p2'], 0.3, 0, 1))

p0_u = uf(99270, 30)
p1_u = unp.uarray(p1, u_p1)
p2_u = unp.uarray(p2, u_p2)

kappa = p1_u/(p1_u - p2_u)

values = unp.nominal_values(kappa)
errors = unp.std_devs(kappa)

weights = 1 / errors**2
mean = np.sum(weights * values) / np.sum(weights)
unc = np.sqrt(1 / np.sum(weights))
unc = unc * StudCoef(0.9973, 9)
kappa_u = uf(mean, unc)

#print(f'Kappa z rozvoje a tlaku je: {kappa_u:.1u}')

kappa = (unp.log((p1_u+p0_u)/p0_u)) / (unp.log((p1_u+p0_u)/(p2_u+p0_u)))

values = unp.nominal_values(kappa)
errors = unp.std_devs(kappa)

weights = 1 / errors**2
mean = np.sum(weights * values) / np.sum(weights)
unc = np.sqrt(1 / np.sum(weights))
unc = unc * StudCoef(0.9973, 9)
kappa_u = uf(mean, unc)

#print(f'Kappa z plneho vypoctu je: {kappa_u:.1u}')

# u trubice
h1 = np.array(df_tlaky['h1'])
h2 = np.array(df_tlaky['h2'])

u_h1 = np.array(unc_B_cteni(1))
u_h2 = np.array(unc_B_cteni(1))

h1_u = unp.uarray(h1, u_h1)
h2_u = unp.uarray(h2, u_h2)

kappa = h1_u/(h1_u - h2_u)

values = unp.nominal_values(kappa)
errors = unp.std_devs(kappa)

weights = 1 / errors**2
mean = np.sum(weights * values) / np.sum(weights)
unc = np.sqrt(1 / np.sum(weights))
unc = unc * StudCoef(0.9973, 9)
kappa_u = uf(mean, unc)

#print(f'Kappa z rozvoje a U trubice je: {kappa_u:.1u}')



# rychlost zvuku ve vzduchu


# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "2065785545"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df_zvuk = pd.read_csv(url)


# linearni fit
def linear_model(x, a, b):
    return a * x + b


# odhad parametru, hranice
R_initial = abs(df_zvuk.loc[0,"f840"] - df_zvuk.loc[1,"f840"])
b_initial = 0
p0 = [R_initial, b_initial]
bounds = (0, np.inf)


# vypocet hodnot pro fit
popt, pcov = curve_fit(linear_model, df_zvuk.index.to_numpy(dtype=float), df_zvuk["f840"], p0=p0, bounds=bounds)
R, b = popt # OPTimalni Parametry -- popt
R_u, b_u = np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice
R = uf(R, R_u)
b = uf(b, b_u)


# graf hodnot
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_title("lambda pul", fontsize=25, pad=15)
ax.set_xlabel(fr"$i$", fontsize=20)
ax.set_ylabel(fr"$D$", fontsize=20)
ax.scatter(df_zvuk.index, df_zvuk["f840"],marker="o",label="Naměřené hodnoty", color="blue", s=100)
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)


# vykresleni fitu
U_fit = np.linspace(df_zvuk["f840"].min(), df_zvuk["f840"].max(), 100)

ax.plot(U_fit, linear_model(U_fit, *popt), label=fr"Lineární fit: $R$ = {R:.1uPL} $\Omega$", color="red")

ax.legend(fontsize=15)
plt.show()