from google.colab import drive
drive.mount('/content/drive', force_remount=True)

import sys
sys.path.append('/content/drive/Shareddrives/Aircraft Engine Project')
import Real_Turbofan_Engine
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from __future__ import print_function
import numpy as np
aircraft = widgets.Box(
    [
        widgets.Label(value='Choose Aircraft:'),
        widgets.RadioButtons(
            options=[
                'Airbus A320',
                'Boeing B737'
            ],
            layout={'width': 'max-content'}
        )
    ]
)
#Weight:
#Aircraft : [Take_off_weight, empty_weight, payload, fuel_capacity] tonnes
weight = {'Airbus A320':[78, 39.5, 16.6,22.84], 'Boeing B737':[70.535, 41.145, 20.882, 21.685] }


#Aircraft: [cd0, k, S] SI units
cd_0 = {'Airbus A320':[0.023, 0.0334, 122.6], 'Boeing B737':[0.024, 0.0366, 102] }

def CL(weight, V, S):
  return (weight*9.80665*2)/(S*0.9*V**2)

def CD(cd_0, k, cl):
  return cd_0 + k*cl**2

#Range
def t_f(cl, cd, tsfc, wi, wf): #wf = wi - fuel capacity
  return (cl/cd)*(1/tsfc)*9.81*np.log(wi/wf)


def range(t_f, V):
  return t_f*V

#Size
#Aircraft: []
range = widgets.ToggleButtons(
    options=['Mumbai' , 'Delhi', 'Kolkata'],
    description='Range:',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltips=['441Km', '775 Km', '1617 Km'],
#     icons=['check'] * 3
)
altitude=widgets.FloatSlider(
    value=35000,
    min=35000,
    max=42000,
    step=100,
    description='Altitude:',
    disabled=False,
    continuous_update=True,
    orientation='vertical',
    readout=True,
    readout_format='.1f',
)
speed=widgets.FloatSlider(
    value=0.5,
    min=0.5,
    max=1,
    step=0.01,
    description='Mach Number',
    disabled=False,
    continuous_update=True,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)
compressor_ratio=widgets.FloatSlider(
    value=10,
    min=10,
    max=35,
    step=0.1,
    description='Compressor Ratio',
    disabled=False,
    continuous_update=True,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)
bypass_ratio=widgets.FloatSlider(
    value=0,
    min=0,
    max=10,
    step=0.1,
    description='Bypass Ratio',
    disabled=False,
    continuous_update=True,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)


fan_pressure_ratio=widgets.FloatSlider(
    value=1,
    min= 1,
    max=5,
    step=0.01,
    description='Fan Pressure Ratio',
    disabled=False,
    continuous_update=True,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)
level_of_tech = widgets.Dropdown(
    options=[('Level 1', 1), ('Level 2', 2), ('Level 3', 3), ('Level 4', 4)],
    value=2,
    description='Level of technology',
)
display(level_of_tech)
efficiency = {'Level 1':[1110, 0.8, 0.95, 0.8, 0.78,0.9,0.95,0.9,0.85 ], 
                    'Level 2':[1390, 0.85, 0.96, 0.84, 0.82,0.95,0.97,0.92,0.91 ],
                    'Level 3':[1780, 0.89, 0.97, 0.88, 0.86,0.98,0.98,0.94,0.98 ],
                    'Level 4':[2000, 0.90, 0.98, 0.90, 0.89,0.995,0.995,0.95,0.99 ]}
if level_of_tech.value==1:
  _T_t4 = efficiency['Level 1'][0]
  _e_t = efficiency['Level 1'][1]
  _eta_m = efficiency['Level 1'][2]
  _e_c = efficiency['Level 1'][3]
  _e_f = efficiency['Level 1'][4]
  _pi_dmax = efficiency['Level 1'][5]
  _pi_n= efficiency['Level 1'][6]
  _pi_b = efficiency['Level 1'][7]
  _eta_b = efficiency['Level 1'][8]

elif level_of_tech.value==2:
  _T_t4 = efficiency['Level 2'][0]
  _e_t = efficiency['Level 2'][1]
  _eta_m = efficiency['Level 2'][2]
  _e_c = efficiency['Level 2'][3]
  _e_f = efficiency['Level 2'][4]
  _pi_dmax = efficiency['Level 2'][5]
  _pi_n= efficiency['Level 2'][6]
  _pi_b = efficiency['Level 2'][7]
  _eta_b = efficiency['Level 2'][8]

elif level_of_tech.value==3:
  _T_t4 = efficiency['Level 3'][0]
  _e_t = efficiency['Level 3'][1]
  _eta_m = efficiency['Level 3'][2]
  _e_c = efficiency['Level 3'][3]
  _e_f = efficiency['Level 3'][4]
  _pi_dmax = efficiency['Level 3'][5]
  _pi_n= efficiency['Level 3'][6]
  _pi_b = efficiency['Level 3'][7]
  _eta_b = efficiency['Level 3'][8]

else :
  _T_t4 = efficiency['Level 4'][0]
  _e_t = efficiency['Level 4'][1]
  _eta_m = efficiency['Level 4'][2]
  _e_c = efficiency['Level 4'][3]
  _e_f = efficiency['Level 4'][4]
  _pi_dmax = efficiency['Level 4'][5]
  _pi_n= efficiency['Level 4'][6]
  _pi_b = efficiency['Level 4'][7]
  _eta_b = efficiency['Level 4'][8]


engine = Real_Turbofan_Engine.TurboFanAnalysis()

engine.setFlightMachNumber(speed.value)
engine.setFlightConditions(altitude.value*0.3048)
engine.setFuelInfo(42.8E6)
engine.setInletOutletProperties(_pi_dmax, 1, _pi_n) #fan nozzle pressure ratio = 1
engine.setBurnerProperties(_pi_b,_eta_b)
engine.setCompressorProperties(compressor_ratio.value, _e_c)
engine.setFanProperties(fan_pressure_ratio.value, _e_f)
engine.setTurbineProperties(_T_t4, _e_t,_eta_m)
engine.setBypassRatio(bypass_ratio.value)

engine.initializeProblem()
engine.performAnalysis()

print(engine.getSpecificThrust())
