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


# nacteni google tabulek
sheet_id = "1SabDjWsPIsUqenpKLWSS_sL0DrfNNjyDOQ5PH-PDqho"
gid = "1924903675"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_infra = pd.read_csv(url)


# emisivita povrchu
t = np.array(df_infra['Ccerna'])
tir = np.array(df_infra['cerna'])

unc_t = unc_B_digital(df_infra['Ccerna'], 1, 1, 1)
unc_tir = unc_B_digital(df_infra['cerna'], 1, 1, 1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)

# funkce na vazeny prumer
def weight_average(hodnota): # hodnota : uarray
    values = unp.nominal_values(hodnota)
    errors = unp.std_devs(hodnota)
    weights = 1 / errors**2
    mean = np.sum(weights * values) / np.sum(weights)
    unc = np.sqrt(1 / np.sum(weights))
    unc = unc * StudCoef(0.9973, 4)
    return uf(mean, unc) # return : ufloat

epsilon = weight_average(epsilon)
#print(f'Epsilon černé desky je: {epsilon:.1u}')


t = np.array(df_infra['Cseda'])
tir = np.array(df_infra['seda'])

unc_t = unc_B_digital(df_infra['Cseda'], 1, 1, 1)
unc_tir = unc_B_digital(df_infra['seda'], 1, 1, 1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)
epsilon = weight_average(epsilon)
#print(f'Epsilon šedé desky je: {epsilon:.1u}')


# propustnost okenek
ir = np.array(df_infra['Ckremik'])
okno = np.array(df_infra['kremik'])

unc_ir = unc_B_digital(df_infra['Ckremik'], 1, 1, 1)
unc_okno = unc_B_digital(df_infra['kremik'], 1, 1, 1)

ir_unc = unp.uarray(ir, unc_ir)
okno_unc = unp.uarray(okno, unc_okno)

tau = ((okno_unc+273.15)**4)/((ir_unc+273.15)**4)
tau = weight_average(tau)
#print(f'Tau křemíku je: {tau:.1u}')


ir = np.array(df_infra['Cnacl'])
okno = np.array(df_infra['nacl'])

unc_ir = unc_B_digital(df_infra['Cnacl'], 1, 1, 1)
unc_okno = unc_B_digital(df_infra['nacl'], 1, 1, 1)

ir_unc = unp.uarray(ir, unc_ir)
okno_unc = unp.uarray(okno, unc_okno)

tau = ((okno_unc+273.15)**4)/((ir_unc+273.15)**4)
tau = weight_average(tau)
#print(f'Tau NaCl je: {tau:.1u}')


# zmrazena ledova deska
t = np.array(df_infra['Cled'])
tir = np.array(df_infra['led'])

unc_t = unc_B_digital(df_infra['Cled'], 1, 1, 1)
unc_tir = unc_B_digital(df_infra['led'], 1, 1, 1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)
epsilon = weight_average(epsilon)
#print(f'Epsilon poledované desky je: {epsilon:.1u}')

t = np.array(df_infra['Cmed'])
tir = np.array(df_infra['med'])

unc_t = unc_B_digital(df_infra['Cmed'], 1, 1, 1)
unc_tir = unc_B_digital(df_infra['med'], 1, 1, 1)

t_unc = unp.uarray(t, unc_t)
tir_unc = unp.uarray(tir, unc_tir)

epsilon = ((tir_unc+273.15)**4)/((t_unc+273.15)**4)
epsilon = weight_average(epsilon)
#print(f'Epsilon měděné desky je: {epsilon:.1u}')


# relaxacni doba

# nacteni google tabulek
sheet_id = "1SabDjWsPIsUqenpKLWSS_sL0DrfNNjyDOQ5PH-PDqho"
gid = "408060846"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df_relax = pd.read_csv(url)


# fit a graf
# graf hodnot
fig, ax = plt.subplots(figsize=(16, 9))
ax.plot(df_relax['cas'], df_relax['napeti'])
plt.show()