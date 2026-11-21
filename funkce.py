# import knihoven
import pandas as pd                             # tabulky, dataframe
import numpy as np                              # array, numericke vypocty
import matplotlib.pyplot as plt                 # grafy
from uncertainties import ufloat as uf          # propagace nejistot
from scipy.optimize import curve_fit            # fitovani
from scipy import stats                         # studentuv koeficient, ...
from uncertainties import unumpy as unp         # numpy + ufloat
from uncertainties import correlated_values     # popt, pcov, korelace


# downloads path
'''
from pathlib import Path
# path config
downloads_dir = Path.home() / 'Downloads'
# ujistime se, ze slozka existuje (kdyby nahodou ne)
downloads_dir.mkdir(parents=True, exist_ok=True)
# output_path = downloads_dir / 'muj_graf.png'
'''


# nacteni google tabulek
sheet_id = 'SPREADSHEET_ID'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
#df = pd.read_csv(url)


# nejistota typu A 
def unc_A(data):
    '''
    Nejistoty typu A

    data : list nebo numpy array
        mereni
    return : float
        nejistota typu A
    '''
    data = np.array(data)
    n = len(data)

    s = np.std(data, ddof=1)
    u_A = s / np.sqrt(n)
    
    return u_A


# nejistoty typu B pro digitalni pristroje
def unc_B_digital(reading, percent_reading, digits, resolution):    # vse musi byt ve spravnych jednotkach; funguje pouze pro jedny podminky zaroven
    '''
    Nejistoty typu B pro digitalni mereni (ponechame krajni)

    reading : float nebo array
        namerena hodnota
    percent_reading : float
        % of reading
    digits : float
        pocet digitu
    resolution : float
        nejmensi dilek
    return : nejistota typu B
    '''
    max_error = abs(reading) * (percent_reading/100) + digits * resolution  # max_error -- krajni nejistota
    u_B = max_error

    return u_B


# nejistota typu B u cteni z nejmensiho dilku
def unc_B_cteni(data):
    '''
    Nejistota typu B pro napr pravitko

    data : float
        nejmensi dilek
    return : float
        nejistota typu B
    '''
    u_B = data/(3**0.5)

    return u_B


# funkce na Studentuv koeficient
def StudCoef(confidence, dof): 
    '''
    Vypocet odpovidajiciho Studentova koeficientu

    confidence : float
        hladina spolehlivosti, typicke hodnoty 0.683, 0.9973;
    dof : int
        pocet stupnu volnosti, pro jednoduchou statistiku array.size-1
    return : float
        Studentuv koeficient pro danou hladinu spolehlivosti a pocet stupnu volnosti
    '''
    alpha = 1 - confidence

    return stats.t.ppf(1 - alpha/2, dof)


# funkce na vazeny prumer
def weight_average(hodnota):
    '''
    hodnota : uarray
        pole s vysledky a jejich nejistotami
    return : ufloat
        vazeny prumer
    '''
    values = unp.nominal_values(hodnota)
    errors = unp.std_devs(hodnota)
    weights = 1 / errors**2
    mean = np.sum(weights * values) / np.sum(weights)
    unc = np.sqrt(1 / np.sum(weights))
    unc = unc * StudCoef(0.9973, 9)

    return uf(mean, unc)


# nacteni z df do numpy
def df_to_numpy_matrix(df, sloupce, dtype=float):
    '''
    df : dataframe
        df ktery prevadime na numpy objekt
    sloupce : list
        jmeno sloupce (str) nebo seznam jmen (list[str])
    return : numpy.matrix
        matice puvodni df tabulky
    '''
    if isinstance(sloupce, str):
        sloupce = [sloupce]

    chybejici = [s for s in sloupce if s not in df.columns]
    if chybejici:
        raise KeyError(f'Chybejici sloupce: {chybejici}')

    data = df[sloupce].to_numpy(dtype=dtype)
    return data[:, 0] if len(sloupce) == 1 else data


# ufloat pro tuple
def tuple_ufloat_unc_A(*velicina):
    list_velicin = [*velicina]
    return tuple(uf(np.mean(v), unc_A(v)) for v in list_velicin)


# ufloat z aritmetickeho prumeru
def ufloat_unc_A(array):
    return uf(np.mean(array), unc_A(array))


# array do latex
def array_to_latex(*array, dig=1, format='u', style='L', only_return=False):
    output = [f'${u:.{dig}{format}{style}}$' for u in array]
    if only_return:
        return output
    else:
        for s in output:
            print(s)


# nacteni z df do jednotlivych arrays
def df_to_arrays(df, sloupce, od=0, do=None, dtype=float):
    if isinstance(sloupce, str):
        sloupce = [sloupce]

    chybejici = [s for s in sloupce if s not in df.columns]
    if chybejici:
        raise KeyError(f'Chybejici sloupce: {chybejici}')

    return [df[s].iloc[od:do].dropna().to_numpy(dtype=dtype) for s in sloupce]


# prepocet z popt a pcov na ufloaty
def popt_pcov_to_ufloat(popt, pcov, correlated=False):
    '''
    Převede výsledek curve_fit (popt, pcov) na ufloaty.

    Parametry
    ---------
    popt : array_like   optimální parametry z curve_fit
    pcov : array_like   kovarianční matice z curve_fit
    correlated : bool   True  -> ufloaty nesou korelace mezi parametry
                        False -> nezávislé ufloaty (jen sqrt diagonály pcov)

    Vrací
    -----
    tuple[ufloat, ...]  parametry s nejistotami
    '''
    popt = np.asarray(popt, dtype=float)
    pcov = np.asarray(pcov, dtype=float)

    if correlated:
        return tuple(correlated_values(popt, pcov))

    perr = np.sqrt(np.diag(pcov))
    return tuple(uf(v, e) for v, e in zip(popt, perr))


# path config
'''
import matplotlib.pyplot as plt
from pathlib import Path

# Cesta do Downloads funguje stejně na Windows i Linuxu
downloads_dir = Path.home() / 'Downloads'

# Ujistíme se, že složka existuje (kdyby náhodou ne)
downloads_dir.mkdir(parents=True, exist_ok=True)

# Příklad grafu
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Uložení - Path se automaticky převede na string se správnými lomítky
output_path = downloads_dir / 'muj_graf.png'
fig.savefig(output_path, dpi=300, bbox_inches='tight')

print(f'Graf uložen do: {output_path}')
'''