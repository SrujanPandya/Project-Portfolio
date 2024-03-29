from shutil import ExecError
import ambiance
import numpy as np
import ipywidgets as widgets

def getGasConstant(gamma, c_p) :
    '''Enter c_p in J / kg - K'''
    return (gamma - 1.0) * c_p / gamma

def getSonicSpeed(gamma, gas_constant, temperature) :
    '''Enter gas_constant in J / kg - K and temperature in kelvin'''
    return np.sqrt(gamma * gas_constant * temperature)

def getStagnationTemperatureRatio(gamma, mach_number) :

    return 1.0 + 0.5 * (gamma - 1.0) * (mach_number**2)

def getStagnationPressureRatio(gamma, mach_number) :

    return np.float_power(
        getStagnationTemperatureRatio(gamma, mach_number),
        gamma / (gamma - 1)
    )

def getRamRecovery(mach_number) :

	# if mach_number <= 1.0 :

	#     return 1.0

	# elif mach_number <= 5.0 :

	#     return 1.0 - 0.075 * np.float_power((mach_number - 1.0), 1.35)

	# else :

	#     return 800.0 / (np.power(mach_number, 4) + 935.0)

	return  np.where(mach_number <= 1.0, 1.0, 
				np.where(mach_number <= 5.0, 1.0 - 0.075 * np.float_power((np.where(mach_number < 1.0, 1.0, mach_number) - 1.0), 1.35),
					800.0 / (np.power(mach_number, 4) + 935.0)
				)
			)


class TurboFanAnalysis :

	def __init__(self) -> None:

		self._initialized = False
		self._analysis_complete = False

		pass

	def setFlightMachNumber(self, mach_number) :

		if np.all(mach_number > 0) :

			self._M_0 = mach_number
			self._analysis_complete = False
			pass

		else :

			raise ValueError('Mach number must be positive. Given value : ' + str(mach_number))

	def setFlightConditions(self, altitude) :
		'''Enter altitude in metres'''

		if np.all(altitude > 0) :

			air = ambiance.Atmosphere(altitude)

			self._T_0 = air.temperature
			self._P_0 = air.pressure
			self._a_0 = air.speed_of_sound

			self._gamma_c   = ambiance.CONST.kappa
			self._R_c       = ambiance.CONST.R
			self._c_pc      = self._gamma_c * self._R_c / (self._gamma_c - 1.0)

			self._analysis_complete = False
			pass

		else :

			raise ValueError('Altitude must be positive. Given value : ' + str(altitude))

	def setFuelInfo(self, 
		heat_generated_from_combustion,
		gamma_of_combustion_products = ambiance.CONST.kappa,
		heat_capacity_of_combustion_products = ambiance.CONST.kappa * ambiance.CONST.R / (ambiance.CONST.kappa - 1.0)
	) :
		'''Enter heat in J / kg and heat capacity in J / kg - K'''

		if gamma_of_combustion_products > 0 :

			self._gamma_t = gamma_of_combustion_products
			self._analysis_complete = False

		else :

			raise ValueError('Gamma must be positive. Given value : ' + str(gamma_of_combustion_products))

		if heat_generated_from_combustion > 0 :

			self._h_PR = heat_generated_from_combustion
			self._analysis_complete = False

		else :

			raise ValueError('Heat generated must be positive. Given value : ' + str(heat_generated_from_combustion))

		if heat_capacity_of_combustion_products > 0 :

			self._c_pt = heat_capacity_of_combustion_products
			self._analysis_complete = False

		else :

			raise ValueError('Heat capacity must be positive. Given value : ' + str(heat_capacity_of_combustion_products))

		pass

	def setTurbineProperties(self,
		inlet_total_temperature,
		polytropic_efficiency = 1.0,
		mechanical_efficiency = 1.0
	) :
		'''Enter temperature in kelvin'''
		if np.all(inlet_total_temperature > 0) :

			self._T_t4 = inlet_total_temperature
			self._analysis_complete = False

		else :

			raise ValueError('Temperature must be positive. Given value : ' + str(inlet_total_temperature))

		if polytropic_efficiency > 0 and polytropic_efficiency <= 1:

			self._e_t = polytropic_efficiency
			self._analysis_complete = False

		else :

			raise ValueError('Efficiency must belong to the interval (0, 1]. Given value : ' + str(polytropic_efficiency))

		if mechanical_efficiency > 0 and mechanical_efficiency <= 1:

			self._eta_m = mechanical_efficiency
			self._analysis_complete = False

		else :

			raise ValueError('Efficiency must belong to the interval (0, 1]. Given value : ' + str(mechanical_efficiency))

		pass

	def setCompressorProperties(self,
		compression_ratio,
		polytropic_efficiency = 1.0
	) :

		if np.all(compression_ratio >= 1) :

			self._pi_c = compression_ratio
			self._analysis_complete = False

		else :

			raise ValueError('Compression ratio must be greater than or equal to 1. Given value : ' + str(compression_ratio))

		if polytropic_efficiency > 0 and polytropic_efficiency <= 1:

			self._e_c = polytropic_efficiency
			self._analysis_complete = False

		else :

			raise ValueError('Efficiency must belong to the interval (0, 1]. Given value : ' + str(polytropic_efficiency))

		pass

	def setFanProperties(self,
		compression_ratio,
		polytropic_efficiency = 1.0
	) :

		if np.all(compression_ratio >= 1) :

			self._pi_f = compression_ratio
			self._analysis_complete = False

		else :

			raise ValueError('Compression ratio must be greater than or equal to 1. Given value : ' + str(compression_ratio))

		if polytropic_efficiency > 0 and polytropic_efficiency <= 1:

			self._e_f = polytropic_efficiency
			self._analysis_complete = False

		else :

			raise ValueError('Efficiency must belong to the interval (0, 1]. Given value : ' + str(polytropic_efficiency))

		pass

	def setInletOutletProperties(self,
		diffuser_max_total_pressure_ratio = 1.0,
		fan_nozzle_total_pressure_ratio = 1.0,
		nozzle_total_pressure_ratio = 1.0
	) :

		if diffuser_max_total_pressure_ratio > 0 and diffuser_max_total_pressure_ratio <= 1 :

			self._pi_dmax = diffuser_max_total_pressure_ratio
			self._analysis_complete = False

		else :

			raise ValueError('Pressure ratio must be in the interval (0,1]. Given value : ' + str(diffuser_max_total_pressure_ratio))

		if fan_nozzle_total_pressure_ratio > 0 and fan_nozzle_total_pressure_ratio <= 1 :

			self._pi_fn = fan_nozzle_total_pressure_ratio
			self._analysis_complete = False

		else :

			raise ValueError('Pressure ratio must be in the interval (0,1]. Given value : ' + str(fan_nozzle_total_pressure_ratio))

		if nozzle_total_pressure_ratio > 0 and nozzle_total_pressure_ratio <= 1 :

			self._pi_n = nozzle_total_pressure_ratio
			self._analysis_complete = False

		else :

			raise ValueError('Pressure ratio must be in the interval (0,1]. Given value : ' + str(nozzle_total_pressure_ratio))

		pass

	def setBurnerProperties(self,
		total_pressure_ratio = 1.0,
		efficiency = 1.0
	) :

		if total_pressure_ratio > 0 and total_pressure_ratio <= 1 :

			self._pi_b = total_pressure_ratio
			self._analysis_complete = False

		else :

			raise ValueError('Pressure ratio must be in the interval (0,1]. Given value : ' + str(total_pressure_ratio))

		if efficiency > 0 and efficiency <= 1:

			self._eta_b = efficiency
			self._analysis_complete = False

		else :

			raise ValueError('Efficiency must belong to the interval (0, 1]. Given value : ' + str(efficiency))

		pass

	def setBypassRatio(self, alpha) :

		if np.all(alpha >= 0) :

			self._alpha = alpha
			self._analysis_complete = False

		else :

			raise ValueError('Mass flow ratio must be greater than or equal to 0. Given value : ' + str(alpha))

		pass

	def initializeProblem(self) :

		attributes = [
			'_alpha',
			'_eta_b',
			'_pi_b',
			'_pi_n',
			'_pi_fn',
			'_pi_dmax',
			'_e_f',
			'_pi_f',
			'_e_c',
			'_pi_c',
			'_eta_m',
			'_e_t',
			'_T_t4',
			'_c_pt',
			'_h_PR',
			'_gamma_t',
			'_c_pc',
			'_gamma_c',
			'_R_c',
			'_a_0',
			'_P_0',
			'_T_0',
			'_M_0'
		]

		for attribute in attributes :

			if not hasattr(self, attribute) :

				raise AttributeError(attribute + ' not initialized.')

		self._initialized = True

		pass

	def _initializeRatios(self) :

		self._tau_r = getStagnationTemperatureRatio(self._gamma_c, self._M_0)
		self._pi_r  = getStagnationPressureRatio(self._gamma_c, self._M_0)

		self._pi_d  = self._pi_dmax * getRamRecovery(self._M_0)
		
		self._tau_l = self._c_pt * self._T_t4 / (self._c_pc * self._T_0)

		self._tau_c = np.float_power(self._pi_c, (self._gamma_c - 1.0) / (self._gamma_c * self._e_c))
		self._tau_f = np.float_power(self._pi_f, (self._gamma_c - 1.0) / (self._gamma_c * self._e_f))

		pass

	def _calculateFuelRatio(self) :

		self._f = (self._tau_l - self._tau_r * self._tau_c) / ((self._eta_b * self._h_PR / (self._c_pc * self._T_0)) - self._tau_l)

		pass

	def _performTurbineEnergyBalance(self) :

		self._tau_t = 1.0 - (1.0 / (self._eta_m * (1 + self._f))) * (self._tau_r / self._tau_l) * (self._tau_c - 1.0 + self._alpha * (self._tau_f - 1.0))
		self._pi_t  = np.float_power(self._tau_t, self._gamma_t / ((self._gamma_t - 1.0) * self._e_t))

		pass

	def _calculateCoreExitConditions(self)	:

		product_pi = self._pi_r * self._pi_d * self._pi_c * self._pi_b * self._pi_t * self._pi_n

		self._P_9 = self._P_0 * product_pi / getStagnationPressureRatio(self._gamma_t, 1.0)

		self._M_9 = 1.0

		self._M_9 = np.where(
			self._P_9 < self._P_0,
			np.sqrt(
				(2.0 / (self._gamma_t - 1.0)) * 
				(np.float_power(product_pi, (self._gamma_t - 1.0) / self._gamma_t) - 1.0)
			),
			1.0
		)

		self._P_9 = np.where(self._P_9 < self._P_0, self._P_0, self._P_9)

		self._R_t = getGasConstant(self._gamma_t, self._c_pt)
		self._T_9 = self._T_0 * (self._tau_l * self._tau_t / getStagnationTemperatureRatio(self._gamma_t, self._M_9)) * (self._c_pc / self._c_pt)
		self._V_9 = self._M_9 * getSonicSpeed(self._gamma_t, self._R_t, self._T_9)

		pass

	def _calculateFanExitConditions(self) :

		product_pi = self._pi_r * self._pi_d * self._pi_f * self._pi_fn

		self._P_19 = self._P_0 * product_pi / getStagnationPressureRatio(self._gamma_c, 1.0)

		self._M_19 = 1.0

		self._M_19 = np.where(
			self._P_19 < self._P_0,
			np.sqrt(
				(2.0 / (self._gamma_c - 1.0)) * 
				(np.float_power(product_pi, (self._gamma_c - 1.0) / self._gamma_c) - 1.0)
			),
			1.0
		)

		self._P_19 = np.where(self._P_19 < self._P_0, self._P_0, self._P_19)

		self._T_19 = self._T_0 * (self._tau_r * self._tau_f / getStagnationTemperatureRatio(self._gamma_c, self._M_19))
		self._V_19 = self._M_19 * self._a_0 * np.sqrt(self._T_19 / self._T_0)

		pass

	def _calculatePerformanceParameters(self) :

		self._V_0 = self._M_0 * self._a_0

		self._ST = (1.0 / (1.0 + self._alpha)) * (
			(1.0 + self._f) * self._V_9 - self._V_0 +
			(1.0 + self._f) * self._R_t * (self._a_0 ** 2) * self._T_9 * (1.0 - (self._P_0 / self._P_9)) / (self._gamma_c * self._R_c * self._T_0 * self._V_9)
		) + (self._alpha / (1.0 + self._alpha)) * (
			self._V_19 - self._V_0 +
			(self._a_0 ** 2) * self._T_19 * (1.0 - (self._P_0 / self._P_19)) / (self._gamma_c * self._T_0 * self._V_19)
		)

		self._TSFC = self._f / ((1.0 + self._alpha) * self._ST)

		Delta_KE = 0.5 * ( (1.0 + self._f) * (self._V_9 ** 2) + self._alpha * (self._V_19 ** 2) - (1.0 + self._alpha) * (self._V_0 ** 2) )

		self._eta_T = Delta_KE / (self._f * self._h_PR)

		self._eta_P = (2 * self._V_0/self._V_9)/(1+(self._V_0/self._V_9)) # (1.0 + self._alpha) * self._ST * self._V_0 / Delta_KE

		pass

	def performAnalysis(self) :

		if self._initialized :

			self._initializeRatios()
			self._calculateFuelRatio()
			self._performTurbineEnergyBalance()
			self._calculateCoreExitConditions()
			self._calculateFanExitConditions()
			self._calculatePerformanceParameters()
			
			self._analysis_complete = True
			pass
		
		else :

			raise ExecError("Analysis needs to be initialized with initializeProblem()")

	def getSpecificThrust(self) :

		if self._analysis_complete :

			return self._ST

		else :

			raise ExecError("Value not evaluated yet. Run performAnalysis()")

	def getThrustSpecificFuelConsumtion(self) :

		if self._analysis_complete :

			return self._TSFC

		else :

			raise ExecError("Value not evaluated yet. Run performAnalysis()")

	def getThermalEfficiency(self) :

		if self._analysis_complete :

			return self._eta_T

		else :

			raise ExecError("Value not evaluated yet. Run performAnalysis()")

	def getPropulsiveEfficiency(self) :

		if self._analysis_complete :

			return self._eta_P

		else :

			raise ExecError("Value not evaluated yet. Run performAnalysis()")




engine = TurboFanAnalysis()

pi_c_widget = widgets.FloatSlider(
	value=10,
	min=10,
	max=35,
	step=0.1,
	description='Compressor Compression Ratio',
	style = {'description_width' : 'initial'},
	disabled=False,
	continuous_update=True,
	orientation='horizontal',
	readout=True,
	readout_format='.1f'
)

pi_f_widget = widgets.FloatSlider(
	value=1.5,
	min=1,
	max=5,
	step=0.01,
	description='Fan Compression Ratio',
	style = {'description_width' : 'initial'},
	disabled=False,
	continuous_update=True,
	orientation='horizontal',
	readout=True,
	readout_format='.1f'
)

alpha_widget = widgets.FloatSlider(
	value=1,
	min=0,
	max=10,
	step=0.1,
	description='Bypass Ratio',
	style = {'description_width' : 'initial'},
	disabled=False,
	continuous_update=True,
	orientation='horizontal',
	readout=True,
	readout_format='.1f'
)

tech_level_widget = widgets.Dropdown(
    options=[('1', 0), ('2', 1), ('3', 2), ('4', 3)],
    value=2,
    description='Level of Technology',
	style = {'description_width' : 'initial'}
)

pi_d_max =	[	0.9,	0.95,	0.98,	0.995	]
e_c = 		[	0.8,	0.84,	0.88,	0.9		]
e_f =		[	0.78,	0.82,	0.86,	0.89	]
pi_b =		[	0.90,	0.92,	0.94,	0.95	]
eta_b =		[	0.85,	0.91,	0.98,	0.99	]
e_t =		[	0.80,	0.85,	0.89,	0.90	]
pi_n =		[	0.95,	0.97,	0.98,	0.995	]
T_t4 = 		[	1110, 	1390, 	1780, 	2000	]

def setUpEngine(V_0, h, alpha, pi_c, pi_f, tech_level) :

	air = ambiance.Atmosphere(h)

	engine.setFlightMachNumber(V_0 / air.speed_of_sound)
	engine.setFlightConditions(h)

	engine.setFuelInfo(42.8E6, 1.29, 1250)
	
	engine.setInletOutletProperties(
		pi_d_max[tech_level],
		pi_n[tech_level],
		pi_n[tech_level]
	)

	engine.setBurnerProperties(pi_b[tech_level], eta_b[tech_level])

	engine.setCompressorProperties(pi_c, e_c[tech_level])

	engine.setFanProperties(pi_f, e_f[tech_level])

	engine.setTurbineProperties(T_t4[tech_level], e_t[tech_level], 0.9)

	engine.setBypassRatio(alpha)

	pass

if __name__ == '__main__' :

	engine = TurboFanAnalysis()

	engine.setFlightMachNumber(np.array([0.8, 0.9, 1.0]))
	engine.setFlightConditions(np.array([5E3, 6E3, 8E3]))
	engine.setFuelInfo(10E8)
	engine.setInletOutletProperties()
	engine.setBurnerProperties()
	engine.setCompressorProperties(25)
	engine.setFanProperties(1.5)
	engine.setTurbineProperties(1600)
	engine.setBypassRatio(5)
	
	engine.initializeProblem()
	engine.performAnalysis()

	print(engine.getSpecificThrust())

	pass
