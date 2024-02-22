import numpy as np
import ipywidgets as widgets

from ambiance import Atmosphere

class Aircraft :

	def __init__(self) -> None:
		
		self.structure_weight = 0.0	# kg
		self.payload_weight = 0.0	# kg
		self.fuel_capacity = 0.0	# kg

		self.fuel_weight = 0.0		# kg

		self.max_engine_diameter = 0.0	# m
		
		self.C_D0 = 0.0
		self.k_1  = 0.0
		self.k_2  = 0.0

		self.wing_planform_area = 0.0	# m2

		self.takeoff_load_factor = 0.0
		self.landing_load_factor = 0.0

		pass

	def getWeight(self) :

		return self.structure_weight + self.payload_weight + self.fuel_weight

	def getDragCoefficient(self, C_L) :

		return self.C_D0 + self.k_1 * (C_L**2) + self.k_2 * C_L

	def getThrust(self, speed, altitude, n = 1.0) :

		L = n * self.getWeight()

		air = Atmosphere(altitude)

		q = 0.5 * air.density * (speed**2)
		
		C_L = L / (q * self.wing_planform_area)
		C_D = self.getDragCoefficient(C_L)

		return q * C_D * self.wing_planform_area

	def getFuelConsumed(self, time, TSFC, speed, altitude, n = 1.0) :

		L = n * self.getWeight()

		air = Atmosphere(altitude)

		q = 0.5 * air.density * (speed**2)
		
		C_L = L / (q * self.wing_planform_area)
		C_D = self.getDragCoefficient(C_L)
		
		EF = (C_L / C_D) * (1 / (TSFC * 9.81))

		return self.getWeight() * (1.0 - np.exp(-time/EF))

boeing737 = Aircraft()
boeing737.fuel_capacity = 21.685E3
boeing737.structure_weight = 41.145E3
boeing737.payload_weight = 20.882E3
boeing737.max_engine_diameter = 2.5
boeing737.C_D0 = 0.024
boeing737.k1 = 0.0366
boeing737.wing_planform_area = 102
boeing737.takeoff_load_factor = 3.04
boeing737.landing_load_factor = 1.2

airbus320 = Aircraft()
airbus320.fuel_capacity = 22.84E3
airbus320.structure_weight = 39.5E3
airbus320.payload_weight = 16.6E3
airbus320.max_engine_diameter = 2.5
airbus320.C_D0 = 0.023
airbus320.k1 = 0.0334
airbus320.wing_planform_area = 122.6
airbus320.takeoff_load_factor = 3.04
airbus320.landing_load_factor = 1.2

aircraft_widget = widgets.ToggleButtons(
	options=[('Airbus A320', airbus320) ,('Boeing 737', boeing737)],
	description='Aircraft:',
	style = {'description_width' : 'initial'},
	disabled=False,
	tooltips=['1', '2']
)
