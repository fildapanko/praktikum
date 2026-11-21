# library imports
import pandas as pd                             # tables, dataframes
import numpy as np                              # arrays, numerical computations
import matplotlib.pyplot as plt                 # plots
from uncertainties import ufloat as uf          # uncertainty propagation
from uncertainties import unumpy as unp         # numpy + ufloat
from uncertainties import correlated_values     # popt, pcov, correlations
from uncertainties import umath                 # math functions for ufloat
from scipy.optimize import curve_fit            # fitting
from scipy import stats                         # Student's coefficient, ...


# downloads path
'''
from pathlib import Path                        # paths in operating system
# path config
downloads_dir = Path.home() / 'Downloads'
# make sure the folder exists (just in case)
downloads_dir.mkdir(parents=True, exist_ok=True)
# output_path = downloads_dir / 'my_plot.png'
'''


# loading Google Sheets
sheet_id = 'SPREADSHEET_ID'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
#df = pd.read_csv(url)


# type A uncertainty
def unc_A(data):
    '''
    Type A uncertainty (standard error of the mean)

    data : list or numpy array
        measurements
    return : float
        type A uncertainty
    '''
    data = np.array(data)
    n = len(data)

    s = np.std(data, ddof=1)
    u_A = s / np.sqrt(n)

    return u_A


# type B uncertainty for digital instruments
def unc_B_digital(reading, percent_reading, digits, resolution):    # everything must be in the correct units; works for a single set of conditions only
    '''
    Type B uncertainty for digital measurements (the limiting/maximum error is kept)

    reading : float or array
        measured value
    percent_reading : float
        % of reading
    digits : float
        number of digits
    resolution : float
        smallest division (least significant digit)
    return : float or array
        type B uncertainty
    '''
    max_error = abs(reading) * (percent_reading/100) + digits * resolution  # max_error -- limiting (maximum) error
    u_B = max_error # divide by (3**0.5) for standard error

    return u_B


# type B uncertainty from reading the smallest division
def unc_B_reading(data):
    '''
    Type B uncertainty for reading from a scale, e.g. a ruler
    (uniform distribution, half-width = smallest division)

    data : float
        smallest division
    return : float
        type B uncertainty
    '''
    u_B = data/(3**0.5)

    return u_B


# Student's coefficient
def StudCoef(confidence, dof):
    '''
    Calculation of the corresponding Student's coefficient

    confidence : float
        confidence level, typical values 0.683, 0.9973
    dof : int
        degrees of freedom, for simple statistics (array.size - 1)
    return : float
        Student's coefficient for the given confidence level and degrees of freedom
    '''
    alpha = 1 - confidence

    return stats.t.ppf(1 - alpha/2, dof)


# weighted average
def weight_average(data, confidence=0.9973, dof=9):
    '''
    Weighted average with weights 1/sigma^2. The resulting uncertainty is
    multiplied by the Student's coefficient for 0.9973 confidence and
    9 degrees of freedom (defaut).

    data : uarray
        array of results and their uncertainties
    return : ufloat
        weighted average
    '''
    values = unp.nominal_values(data)
    errors = unp.std_devs(data)
    weights = 1 / errors**2
    mean = np.sum(weights * values) / np.sum(weights)
    unc = np.sqrt(1 / np.sum(weights))
    unc = unc * StudCoef(confidence, dof)

    return uf(mean, unc)


# loading from df into numpy, needs .T for the correct allocation
def df_to_numpy_matrix(df, column, dtype=float):
    '''
    Converts the selected columns of a dataframe to a numpy array

    df : dataframe
        dataframe to be converted to a numpy object
    column : str or list[str]
        column name (str) or list of column names (list[str])
    dtype : type
        data type of the resulting array (default float)
    return : numpy.ndarray
        matrix of the selected columns; 1D array if a single column is given
    '''
    if isinstance(column, str):
        column = [column]

    missing = [s for s in column if s not in df.columns]
    if missing:
        raise KeyError(f'Missing columns: {missing}')

    data = df[column].to_numpy(dtype=dtype)

    return data[:, 0] if len(column) == 1 else data


# ufloat for several datasets
def tuple_ufloat_unc_A(*data):
    '''
    Converts each input dataset to a ufloat (arithmetic mean +- type A uncertainty)

    *data : list or numpy array
        one or more datasets of measurements
    return : tuple(ufloat, ...)
        one ufloat per dataset
    '''
    data_list = [*data]

    return tuple(uf(np.mean(v), unc_A(v)) for v in data_list)


# array to LaTeX
def uarray_to_latex(*array, digit=1, format='u', style='L', only_return=False):
    '''
    Formats ufloats as LaTeX strings (e.g. $1.23 \\pm 0.04$)

    *array : ufloat
        one or more ufloats to format
    digit : int
        number of digits / precision in the format specification
    format : str
        ufloat format type (e.g. 'u' for the uncertainty in parentheses)
    style : str
        output style; 'L' for LaTeX
    only_return : bool
        True  -> return the list of strings
        False -> print each string
    return : list[str] or None
        formatted strings if only_return=True, otherwise None
    '''
    output = [f'${u:.{digit}{format}{style}}$' for u in array]
    if only_return:
        return output
    else:
        for s in output:
            print(s)


# loading from df into individual arrays
def df_to_arrays(df, column, first_row=0, last_row=None, dtype=float):
    '''
    Extracts the selected columns of a dataframe as separate numpy arrays.
    NaN values are dropped from each column.

    df : dataframe
        source dataframe
    column : str or list[str]
        column name (str) or list of column names (list[str])
    first_row : int
        first row (index) to include
    last_row : int or None
        row (index) at which to stop (exclusive); None = until the end
    dtype : type
        data type of the resulting arrays (default float)
    return : list[numpy.ndarray]
        one array per column
    '''
    if isinstance(column, str):
        column = [column]

    missing = [s for s in column if s not in df.columns]
    if missing:
        raise KeyError(f'Missing columns: {missing}')

    return [df[s].iloc[first_row:last_row].dropna().to_numpy(dtype=dtype) for s in column]


# conversion from popt and pcov to ufloats
def popt_pcov_to_ufloat(popt, pcov, correlated=False):
    '''
    Converts the result of curve_fit (popt, pcov) to ufloats.

    popt : array_like
        optimal parameters from curve_fit
    pcov : array_like
        covariance matrix from curve_fit
    correlated : bool
        True  -> ufloats carry correlations between parameters
        False -> independent ufloats (only sqrt of the pcov diagonal)
    return : tuple(ufloat, ...)
        parameters with uncertainties
    '''
    popt = np.asarray(popt, dtype=float)
    pcov = np.asarray(pcov, dtype=float)

    if correlated:
        return tuple(correlated_values(popt, pcov))

    perr = np.sqrt(np.diag(pcov))

    return tuple(uf(v, e) for v, e in zip(popt, perr))


# path config again
'''
import matplotlib.pyplot as plt
from pathlib import Path

# The path to Downloads works the same on Windows and Linux
downloads_dir = Path.home() / 'Downloads'

# Make sure the folder exists (just in case)
downloads_dir.mkdir(parents=True, exist_ok=True)

# Example plot
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Saving - Path is automatically converted to a string with the correct slashes
output_path = downloads_dir / 'my_plot.png'
fig.savefig(output_path, dpi=300, bbox_inches='tight')

print(f'Plot saved to: {output_path}')
'''
