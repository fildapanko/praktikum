# import knihoven
import math
import numpy as np
from uncertainties import ufloat
from uncertainties.umath import *
from scipy import stats

def StudCoef(confidence, dof): 
    #Parameters
    #----------
    #confidence : float
    #    hladina spolehlivosti, typicke hodnoty 0.683, 0.9973;
    #dof : 
    #    pocet stupnu volnosti, pro jednoduchou statistiku array.size-1

    #Returns
    #-------
    #float
    #    Studentuv koeficient pro danou hladinu spolehlivosti a pocet stupnu volnosti 
    alpha = 1 - confidence
    return stats.t.ppf(1 - alpha/2, dof) 

#---------------------------------------------------------------------------
#zadani namerenych hodnot
#----------------------------------------------------------------------------
xi = np.array([40.20, 40.20, 40.22, 40.24, 40.24, 40.20, 40.22, 40.24, 40.20, 40.22]) # D vnejsi prumer v mm
yi = np.array([19.00, 18.96, 19.02, 18.96, 18.94, 18.98, 19.00, 18.98, 18.96, 18.98]) # d prumer diry v mm
c = np.array([23.10, 23.14, 23.12, 23.14, 23.12, 23.10, 23.08, 23.10, 23.14, 23.12])  # h vyska v mm
m = 191.551 #hmotnost v gram
#----------------------------------------------------------------------------
#urceni nejistot typu A primych mereni
#----------------------------------------------------------------------------
u_A_x = xi.std(ddof=1)/xi.size**0.5
u_A_y = yi.std(ddof=1)/yi.size**0.5
u_A_C = c.std(ddof=1)/c.size**0.5
u_A_m = 0

#----------------------------------------------------------------------------
#urceni nejistot typu B primych mereni
#----------------------------------------------------------------------------
u_B_x = 0.02/(3**0.5)  #mm
u_B_y = 0.02/(3**0.5)  #mm
u_B_C = 0.02/(3**0.5)  #mm
u_B_m = 0.01/3         #g 

#''' ---------------------------------------------------------------------------
#vypocet kombinovanych nejistot
#----------------------------------------------------------------------------'''
u_C_x = (u_A_x**2 + u_B_x**2)**0.5
u_C_y = (u_A_y**2 + u_B_y**2)**0.5
u_C_C = (u_A_C**2 + u_B_C**2)**0.5
u_C_m = (u_A_m**2 + u_B_m**2)**0.5

#''' ---------------------------------------------------------------------------
#vytvoreni hodnot typu ufloat z vysledku primo merenych velicin a vypis 
#vysledku na jedno platne misto nejistoty, pozor, nejistota je vypisovana s +/-,
#i kdyz je nerozsirena
#----------------------------------------------------------------------------'''
x = ufloat( xi.mean(), u_C_x)
y = ufloat( yi.mean(), u_C_y)
C = ufloat( c.mean(), u_C_C)
m = ufloat(m, u_C_m)

print(f"x = {x:.1u} mm")
print(f"y = {y:.1u} mm")
print(f"C = {C:.1u} mm")
print(f"m = {m:.1u} g")

#'''
#poznamka: vypocet je rozepsan pro nazornost, lze sestavit jednim radkem , napr.
# x = ufloat( xi.mean(), (xi.std(ddof=1)**2/xi.size + u_B_x**2)**0.5)'''


#''' ---------------------------------------------------------------------------
#prevedeni hodnoty i nejistoty do zakladnich jednotek
#----------------------------------------------------------------------------'''
x = x * 1e-3
y = y * 1e-3
C = C * 1e-3
m = m * 1e-3


#''' ---------------------------------------------------------------------------
#vypocet neprimo merene veliciny vcetne standardni nejistoty
#----------------------------------------------------------------------------'''
Z = (4*m)/(math.pi*((x**2)-(y**2))*C)
print(f"uncertainties: Z = {Z:.1u} ")

#''' ---------------------------------------------------------------------------
#vysledek vcetne rozsirene nejistoty
#----------------------------------------------------------------------------'''
confidence = 0.9973
effdof =  min(xi.size, yi.size)-1 # odhad efektivniho poctu stupnu volnosti
Z2 = ufloat(Z.n, Z.s*StudCoef(confidence, effdof))
print(f"uncertainties: Z = {Z2:.1u} ( p = {confidence*100:0.1f}%, \u03BD = {effdof})")