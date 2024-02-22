import os
import numpy as np
import matplotlib.pyplot as plt

from Real_Turbofan_Engine import TurboFanAnalysis
from matplotlib.animation import FuncAnimation
from Non_Dominated_Sorting import sort_vectors
from Genetic_Algorithm import Genetic_Algorithm

MAX_ITER = 30

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

# alpha, pi_c, pi_f, M_0, h, T_t4

max_values = np.array([10.0, 35.0, 5.0, 1.0, 15E3, 2000.0])
min_values = np.array([ 0.0,  1.0, 1.0, 0.5,  5E3,  800.0])
resolution = np.array([ 0.1,  0.1, 0.1, 0.1,  1E2,   10.0])

num_bits = np.array( np.ceil( np.log2( (max_values - min_values) / resolution ) ), dtype=int) + 1
print(sum(num_bits))
bits_conversion_array = [np.power(2, np.arange(bits)) for bits in num_bits]

def bits_to_input(bits) :

	i = 0
	j = num_bits[0]
	alpha = min_values[0] + (max_values[0] - min_values[0]) * np.sum(bits[:, i:j] * bits_conversion_array[0], axis=1) / (2**num_bits[0] - 1)

	i = j
	j += num_bits[1]
	pi_c = min_values[1] + (max_values[1] - min_values[1]) * np.sum(bits[:, i:j] * bits_conversion_array[1], axis=1) / (2**num_bits[1] - 1)

	i = j
	j += num_bits[2]
	pi_f = min_values[2] + (max_values[2] - min_values[2]) * np.sum(bits[:, i:j] * bits_conversion_array[2], axis=1) / (2**num_bits[2] - 1)

	i = j
	j += num_bits[3]
	M_0 = min_values[3] + (max_values[3] - min_values[3]) * np.sum(bits[:, i:j] * bits_conversion_array[3], axis=1) / (2**num_bits[3] - 1)

	i = j
	j += num_bits[4]
	h = min_values[4] + (max_values[4] - min_values[4]) * np.sum(bits[:, i:j] * bits_conversion_array[4], axis=1) / (2**num_bits[4] - 1)

	i = j
	j += num_bits[5]
	T_t4 = min_values[5] + (max_values[5] - min_values[5]) * np.sum(bits[:, i:j] * bits_conversion_array[5], axis=1) / (2**num_bits[5] - 1)

	engine.setBypassRatio(alpha)
	engine.setCompressorProperties(pi_c)
	engine.setFanProperties(pi_f)
	engine.setFlightMachNumber(M_0)
	engine.setFlightConditions(h)
	engine.setTurbineProperties(T_t4)

	engine.performAnalysis()

	pass

def fitness_function(bits) :

	bits_to_input(bits)

	return np.column_stack((engine.getSpecificThrust(), - engine.getThrustSpecificFuelConsumtion()))

problem = Genetic_Algorithm()

problem.set_dimensions(sum(num_bits), 2)
problem.set_number_of_chromosomes(1000)
problem.set_probabilities(0.8, 0.1)
problem.set_fitness_function(fitness_function)
problem.set_sorting_function(sort_vectors)

problem.begin()

Pareto_fronts = []
Other_chromosomes = []

for i in range(MAX_ITER) :
    
    problem.iterate()
    Pareto_fronts.append(problem.get_Pareto_Front_fitness_values())
    Other_chromosomes.append(problem.get_non_Pareto_Front_fitness_values())

problem.stop_iterations()

# print(Pareto_fronts)
# print(num_points_in_Pareto_fronts)

plt.style.use('dark_background')

fig, ax = plt.subplots()

# manager = plt.get_current_fig_manager()
# manager.window.showMaximized()

points, = ax.plot(  Pareto_fronts[0][:, 0], 
                    -Pareto_fronts[0][:, 1],
                    'bo', ms=5, color='yellow',
                    label='Points on Pareto Front')

other_points, = ax.plot(    Other_chromosomes[0][:, 0],
                            -Other_chromosomes[0][:, 1],
                            'bo', ms=3, color='lavender',
                            label='Points not on Pareto Front')

# set axes labels
ax.set_xlabel(r'Specific Thrust (in $\frac{N}{kg/s}$)', fontsize=15)
ax.set_ylabel(r'Thrust Specific Fuel Consumption (in $\frac{kg/s}{N}$)', fontsize=15)

ax.set_ylim([0, np.max(-Other_chromosomes[0][:, 1])])

# set title
ax.set_title('Pareto Front at Generation # 0', fontsize=15)

# Grid
ax.minorticks_on()
ax.grid(which='minor', ls='--', c='green', alpha=0.5)

ax.grid(which='major', c='grey', alpha=0.5)

# Legend
ax.legend(fontsize=15, loc=2)

def animate(i) :

    # set title
    ax.set_title('Pareto Front at Generation # ' + str(i+1), fontsize=15)

    # print(Pareto_fronts[i])
    points.set_data(Pareto_fronts[i][:, 0], -Pareto_fronts[i][:, 1])
    other_points.set_data(Other_chromosomes[i][:, 0], -Other_chromosomes[i][:, 1])
    # points.set_markersize(10)

    return points, other_points, 

anim = FuncAnimation(fig, animate, frames=MAX_ITER, interval=5E3/MAX_ITER)

plt.show()

ch = input('Save ?\n')

if ch == 'y' :
    # save the animation
    print('Saving...')
    anim.save('NSGA_Floor_Optimization_Small_Mutation.mp4', writer = 'ffmpeg', fps = 3)
    print('Done')


best_genes = problem.get_Pareto_Front_chromosomes()

bits_to_input(best_genes)

ax = plt.axes()

ax.plot(engine.getSpecificThrust(), engine.getThrustSpecificFuelConsumtion(), 'bo', color='yellow', ms=5)

# set axes labels
ax.set_xlabel('Length of Laboratory Space (in ft.)', fontsize=15)
ax.set_ylabel('Width of Meeting Space (in ft.)', fontsize=15)

# set title
ax.set_title('Solutions on Pareto Front', fontsize=15)

# Grid
ax.minorticks_on()
ax.grid(which='minor', ls='--', c='green', alpha=0.5)

ax.grid(which='major', c='grey', alpha=0.5)

plt.show()
