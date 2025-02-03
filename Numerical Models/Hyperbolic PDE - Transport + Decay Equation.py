import matplotlib.pyplot as plt
import numpy as np
import math

x_lower = 0
x_upper = 1000
x_interval = 400
dx = (x_upper-x_lower)/(x_interval)
f_lambda = 0.1
dt = dx*f_lambda
t_steps = 2500
initial_t = 0
x_range = np.arange(x_lower,x_upper,dx)

# the PDE is written as it follows:
# U_t + A*U_x + B*U = 0

# Where each component is described in these forms:
# U_t = {U(x,t+1)-0.5*U(x+1,t)-0.5*U(x-1,t)}/dt
# U_x = {U(x+1,t)-U(x-1,t)}/(2*dx)
# A Lax-Friedrichs Finite Difference Scheme will be assembled (hence the lambda)

A_factor = 1  # How fast the solution moves
B_factor = 0#.001  # How fast the solution decays
pi = math.pi

# A and B can be variables, depending of U, x and t.
# For now, they're constants.
# Note: the Courant-Friedrichs-Lewy Condition must be considered!
# -> abs(A_factor*f_lambda) <= 1

# create matrices
mbase = np.zeros(shape=(x_interval,x_interval))
np.fill_diagonal(mbase, - B_factor*dt)
initial_u = 7 - 0.0001*x_range
xmin = 0
xmax = 14

for i in range(0,x_interval-1):
    mbase[i,(i+1)] = 0.5 - 0.5*(A_factor*dt/dx)
    mbase[(i+1),i] = 0.5 + 0.5*(A_factor*dt/dx)

u_prev = initial_u
t_prev = initial_t

for i in range(0,t_steps):
    t_prev = t_prev + dt
    f_vector = np.zeros(shape=(x_interval))
    f_vector[0] = 7 + math.sin(t_prev/5)
    ans = np.dot(mbase,u_prev) + dt*f_vector
    u_prev = ans
    x = np.asarray(x_range)
    y = np.asarray(ans)
    tx = i % 5
    if (tx == 0):
        plt.plot(x,y)
        plt.ylim(xmin,xmax)
        plt.title('Timestep No. '+str(np.round(t_prev,3)))
        plt.show()
        

