from turtle import speed
from matplotlib import style
import numpy as np
import ipywidgets as widgets

from Aircraft import Aircraft

class Mission :

	def __init__(self) -> None:
		
		self.range = 0.0	# m
		self.speed = 0.0	# m / s
		self.altitude = 0.0	# m

		pass

	def getThrustRequirements(self, aircraft, fuel_weight, TSFC = 1.0E-6) :

		aircraft.fuel_weight = fuel_weight

		thrust_takeoff_ground = aircraft.getThrust(self.speed, 0, aircraft.takeoff_load_factor)

		takeoff_time = self.altitude / (self.speed / np.sqrt(10))

		fuel_consumed = aircraft.getFuelConsumed(takeoff_time, TSFC, self.speed, self.altitude / 2.0, aircraft.takeoff_load_factor)

		aircraft.fuel_weight -= fuel_consumed

		thrust_takeoff_cruise = aircraft.getThrust(self.speed, self.altitude, aircraft.takeoff_load_factor)

		thrust_cruise_initial = aircraft.getThrust(self.speed, self.altitude)

		total_fuel_consumed = fuel_consumed

		cruise_time = (self.range - 2 * 3 * self.altitude) / self.speed
		
		fuel_consumed = aircraft.getFuelConsumed(cruise_time, TSFC, self.speed, self.altitude)

		total_fuel_consumed += fuel_consumed
		aircraft.fuel_weight -= fuel_consumed

		thrust_cruise_final = aircraft.getThrust(self.speed, self.altitude)

		thrust_landing_cruise = aircraft.getThrust(self.speed, self.altitude, aircraft.landing_load_factor)

		fuel_consumed = aircraft.getFuelConsumed(takeoff_time, TSFC, self.speed, self.altitude / 2.0, aircraft.landing_load_factor)

		aircraft.fuel_weight -= fuel_consumed
		total_fuel_consumed += fuel_consumed

		thrust_landing_ground = aircraft.getThrust(self.speed, 0, aircraft.landing_load_factor)

		return (total_fuel_consumed, [
			thrust_takeoff_ground,
			thrust_takeoff_cruise,
			thrust_cruise_initial,
			thrust_cruise_final,
			thrust_landing_cruise,
			thrust_landing_ground
		])

range_widget = widgets.FloatSlider(
	value=400,
	min=400,
	max=2000,
	step=50,
	description='Range (km)',
	style = {'description_width' : 'initial'},
	disabled=False,
	continuous_update=True,
	orientation='horizontal',
	readout=True,
	readout_format='.1f'
)

altitude_widget = widgets.FloatSlider(
	value=35000,
	min=35000,
	max=42000,
	step=100,
	description='Altitude (ft)',
	style = {'description_width' : 'initial'},
	disabled=False,
	continuous_update=True,
	orientation='horizontal',
	readout=True,
	readout_format='.1f'
)

speed_widget = widgets.FloatSlider(
	value=1000,
	min=700,
	max=1300,
	step=0.01,
	description='Speed (km/hr)',
	style = {'description_width' : 'initial'},
	disabled=False,
	continuous_update=True,
	orientation='horizontal',
	readout=True,
	readout_format='.1f'
)