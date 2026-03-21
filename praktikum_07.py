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


# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "0"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df_tlaky = pd.read_csv(url)


# tlakomer
p1 = np.array(df_tlaky['p1'])
p2 = np.array(df_tlaky['p2'])

u_p1 = np.array(unc_B_digital(df_tlaky['p1'], 0.3, 0, 1)) 
u_p2 = np.array(unc_B_digital(df_tlaky['p2'], 0.3, 0, 1))

p0_u = uf(99270, 30)
p1_u = unp.uarray(p1, u_p1)
p2_u = unp.uarray(p2, u_p2)

kappa = p1_u/(p1_u - p2_u)


# funkce na vazeny prumer
def weight_average(hodnota): # krajni
    values = unp.nominal_values(hodnota)
    errors = unp.std_devs(hodnota)
    weights = 1 / errors**2
    mean = np.sum(weights * values) / np.sum(weights)
    unc = np.sqrt(1 / np.sum(weights))
    unc = unc * StudCoef(0.9973, 9)
    return uf(mean, unc)

kappa_u = weight_average(kappa)
print(f'Kappa z rozvoje a tlaku je: {kappa_u:.1u}')

kappa = (unp.log((p1_u+p0_u)/p0_u)) / (unp.log((p1_u+p0_u)/(p2_u+p0_u)))
kappa_u = weight_average(kappa)
print(f'Kappa z plneho vypoctu je: {kappa_u:.1u}')


# u trubice
h1 = np.array(df_tlaky['h1'])
h2 = np.array(df_tlaky['h2'])

u_h1 = np.array(unc_B_cteni(1))
u_h2 = np.array(unc_B_cteni(1))

h1_u = unp.uarray(h1, u_h1)
h2_u = unp.uarray(h2, u_h2)

kappa = h1_u/(h1_u - h2_u)
kappa_u = weight_average(kappa)
print(f'Kappa z rozvoje a U trubice je: {kappa_u:.1u}')



# rychlost zvuku ve vzduchu


# nacteni google tabulek
sheet_id = "1GyY4H-OTBL_kVIBzqRwe_UpJX8blSdwkcHyNo-NSDso"
gid = "2065785545"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df_zvuk = pd.read_csv(url)


# linearni fit
def linear_model(x, a, b):
    return a * x + b

values = []
errors = []

# funkce na fitovani
def fit_lin_plot(df, column, barva):
    col = df[f'{column}'].dropna()
    popt, pcov = curve_fit(linear_model, df.index[:len(col)].to_numpy(dtype=float)+1, col,p0=None, bounds=(-np.inf, np.inf))
    A, b = popt # OPTimalni Parametry -- popt
    A_u, b_u = np.sqrt(np.diag(pcov)) # nejistota parametru z kovariancni matice

    values.append(abs(A*1e-3))
    errors.append(abs(A_u*1e-3))

    A = uf(A, A_u)
    b = uf(b, b_u)

    U_fit = np.linspace(1, len(col), 100)
    ax.plot(U_fit, linear_model(U_fit, *popt), label=fr"Lineární fit: $\lambda / 2$ = {A:.1uPL} $mm$", color=f"{barva}")



# graf hodnot
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_title("Poloha maxim $D_i$", fontsize=25, pad=15)
ax.set_xlabel(fr"$i$", fontsize=20)
ax.set_ylabel(fr"$D (mm)$", fontsize=20)
ax.scatter(df_zvuk.index+1, df_zvuk["f840"],marker="o",label="Frekvence 840 $Hz$", color="blue", s=100)
ax.scatter(df_zvuk.index+1, df_zvuk["f995"],marker="o",label="Frekvence 995 $Hz$", color="red", s=100)
ax.scatter(df_zvuk.index+1, df_zvuk["f1095"],marker="o",label="Frekvence 1095 $Hz$", color="green", s=100)
ax.scatter(df_zvuk.index+1, df_zvuk["f1255"],marker="o",label="Frekvence 1255 $Hz$", color="purple", s=100)
ax.tick_params(labelsize=15)
ax.grid(True, alpha=0.7)


# vykresleni fitu
fit_lin_plot(df_zvuk, 'f840', '#0072B2')
fit_lin_plot(df_zvuk, 'f995', "#D55E00")
fit_lin_plot(df_zvuk, 'f1095', '#009E73')
fit_lin_plot(df_zvuk, 'f1255', '#CC79A7')

ax.legend(fontsize=15)
#plt.savefig(r"C:\Users\Admin\Downloads\lambdapul.png", dpi=300)
#plt.show()


# vypocet kappy z fitu
lambda2 = unp.uarray(values , errors)
freq = np.array([840, 995, 1095, 1255])
rho = 1.167065

kappa = (rho * 4 * (lambda2**2) * freq**2)/p0_u
kappa_u = weight_average(kappa)
print(f'Kappa z fitu je: {kappa_u:.1u}')