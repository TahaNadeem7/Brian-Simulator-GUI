# Models
# See ~/ICL/repos/notebooks/Brian2gui/cells.py for more models

__all__ = ['NEURON_MODELS', 'SYNAPSE_MODELS']

LIF = '''dv/dt = (v0 - v) / tau : volt (unless refractory)
v0 : volt'''

# https://groups.google.com/forum/#!topic/briansupport/MW1z67jMf1g
Izh = '''dv/dt = (0.04/ms/mV)*v**2 + (5/ms) * v + 140*mV/ms - u + I_syn/ms + I_in/ms : volt
du/dt = a*((b*v) - u) : volt/second
dx/dt = -x/(1*ms) : 1
I_in = ceil(x)*(x>(1/exp(1)))*amplitude : volt
dI_syn/dt = - I_syn/tau : volt
a : 1/second
b : 1/second
c : volt
d : volt/second
amplitude : volt
tau : ms'''

# Introduced in Brette R. and Gerstner W. (2005), Adaptive Exponential
# Integrate-and-Fire Model as an Effective Description of Neuronal Activity,
# J. Neurophysiol. 94: 3637 - 3642.
# https://brian2.readthedocs.io/en/latest/examples/frompapers.Brette_Gerstner_2005.html
AdExp = '''dvm/dt = (gL*(EL - vm) + gL*DeltaT*exp((vm - VT)/DeltaT) + I - w)/C : volt
dw/dt = (a*(vm - EL) - w)/tauw : amp
I : amp'''

# https://brian2.readthedocs.io/en/2.0rc3/examples/IF_curve_Hodgkin_Huxley.html
HH = '''dv/dt = (gl*(El-v) - g_na*(m*m*m)*h*(v-ENa) - g_kd*(n*n*n*n)*(v-EK) + I)/Cm : volt
dm/dt = 0.32*(mV**-1)*(13.*mV-v+VT) /
    (exp((13.*mV-v+VT)/(4.*mV))-1.)/ms*(1-m)-0.28*(mV**-1)*(v-VT-40.*mV)/
    (exp((v-VT-40.*mV)/(5.*mV))-1.)/ms*m : 1
dn/dt = 0.032*(mV**-1)*(15.*mV-v+VT) /
    (exp((15.*mV-v+VT)/(5.*mV))-1.)/ms*(1.-n)-.5*exp((10.*mV-v+VT)/(40.*mV))/ms*n : 1
dh/dt = 0.128*exp((17.*mV-v+VT)/(18.*mV)) / ms*(1.-h)-4./(1+exp((40.*mV-v+VT)/(5.*mV)))/ms*h : 1
I : amp'''

NEURON_MODELS = {
    'Blank': {'model': '', 'threshold': '', 'reset': '', 'refractory': ''},
    'Leaky Integrate & Fire': {'model': LIF, 'threshold': 'v > 10*mV', 'reset': 'v = 0*mV', 'refractory': '5*ms'},
    'Adaptive exponential I&F': {'model': AdExp, 'threshold': 'vm > Vcut', 'reset': 'vm = Vr; w += b', 'refractory': ''},
    'Izhikevich': {'model': Izh, 'threshold': 'v > 30*mV', 'reset': '''v = c; u += d''', 'refractory': ''},
    'Hodgkin-Huxley': {'model': HH, 'threshold': 'v > -40*mV', 'reset': '', 'refractory': 'v > -40*mV'}
}

SYNAPSE_MODELS = {}


#from collections import namedtuple
#Neuron = namedtuple('Neuron', ['model', 'threshold', 'reset', 'refractory'])
#Neuron.__doc__ += ': Neuron model'
#Neuron.model.__doc__ = 'Differential equations describing the cell membrane potential'
#Neuron.threshold.__doc__ = 'Firing threshold'
#...
#LIFneuron = Neuron(model=LIF, threshold='v > 10*mV', reset='v = 0*mV', refractory='5*ms')
##LIFneuron._asdict()  # Return OrderedDict
##NewLIF = LIFneuron._replace(refractory='2*ms')  # New instance of namedtuple replacing the value of refractory
