import matplotlib.pyplot as plt
import numpy as np
import math

# the PDE is written as it follows:
# U_t + A*U_x + B*U = f(x,t)
# Where each component is described in these forms:
# U_t = {U(x,t+1)-0.5*U(x+1,t)-0.5*U(x-1,t)}/dt
# U_x = {U(x+1,t)-U(x-1,t)}/(2*dx)
# A Lax-Friedrichs Finite Difference Scheme will be assembled 

# setting values for PDE constants A and B (cannot be zero!)
# A and B can be variables, depending of U, x and t.
# For now, they're constants.
A_factor = 3  # How fast the solution moves
B_factor = 0.001  # How fast the solution decays

# setting x-domain
x_lower = 0
x_upper = 1000
x_interval = 400
dx = (x_upper-x_lower)/(x_interval-1) # there is no x-axis restriction
x_range = np.linspace(x_lower, x_upper,x_interval)
# Note: boundary values can be inside the x-range, this is not a BVP

# Stability conditions for dt are submitted to the
# Courant-Friedrichs-Lewy Condition -> abs(A_factor*f_lambda) <= 1
critical_lambda = 1/abs(A_factor)
f_lambda = 0.5*critical_lambda
dt = dx*f_lambda
timesteps = 3600
initial_t = 0

# Matrix creation
mbase = np.zeros(shape=(x_interval,x_interval))
np.fill_diagonal(mbase, - B_factor*dt)
initial_u = 7 + np.sin(x_range*(math.pi/(x_upper-x_lower)))*2
x_min = 0
x_max = max(initial_u)

for i in range(0,x_interval-1):
    mbase[i,(i+1)] = 0.5 - 0.5*(A_factor*dt/dx)
    mbase[(i+1),i] = 0.5 + 0.5*(A_factor*dt/dx)

u_prev = initial_u
t_prev = initial_t

for i in range(0,timesteps):
    t_prev = t_prev + dt
    ans = np.dot(mbase,u_prev)
    u_prev = ans
    x = np.asarray(x_range)
    y = np.asarray(ans)
    tx = i % 5
    if (tx == 0):
        plt.plot(x,y)
        plt.ylim(x_min,x_max)
        plt.title('t= '+str(np.round(t_prev,3)))
        plt.show()
        

