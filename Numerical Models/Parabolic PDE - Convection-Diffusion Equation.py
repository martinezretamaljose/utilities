import matplotlib.pyplot as plt
import numpy as np
import math

# the related PDE is written as it follows (Strikwerda, 2004):
# U_t + A*U_x = B*U_xx (1)
# or U_t + A*U_x = B*U_xx - C*U (1a)
# Each component of (1) can be described in these finite difference forms:
# U_t  = {U(x,t+1)-U(x,t)}/dt
# U_x  = {U(x+1,t)-u(x-1,t)}/2*dx
# U_xx = {U(x+1,t)-2*U(x,t)+U(x-1,t)}/dx^2
# these equation types are boundary-value problems (BVP), i.e. we should know
# how U(x,t) behaves in the boundary values of the x-axis domain. 

# setting values for PDE constants A and B (cannot be zero!)
A_factor = 1
B_factor = 5
# setting decay factor (what if the whole whing decays?)
C_factor = 0#.0025

# setting x-domain
x_lower = 0
x_upper = 1000
# There is a condition for dx which indicates that dx must be
# equal or lower than 2*B_factor/A_factor.
critical_n_x = (A_factor*(x_upper - x_lower)/(2*B_factor)) - 1
x_interval = int(divmod(critical_n_x, 1)[0]) + 1 
dx = (x_upper-x_lower)/(x_interval+1)
x_range = np.arange(x_lower+dx,x_upper,dx)
# Note: boundary values cannot be inside the x-range!

# stability condition for t-range
stability_factor = 0.1 #this value must be equal or lower than 0.5
dt = stability_factor*(dx*dx)/B_factor
t_0 = 0    # initial time
t_f = 3600 # final time
timesteps = int(divmod((t_f-t_0)/dt,1)[0] + 1) # the amount of iterations

# boundary functions
def initial_boundary(t):
    ib_ans = 250 + math.sin(t/36)*25
    return(ib_ans)

def final_boundary(t):
    fb_ans = 0 #
    return(fb_ans)

# Matrix creation
mbase = np.zeros(shape=(x_interval,x_interval))
np.fill_diagonal(mbase, 1 - 2*B_factor*dt/(dx*dx) - C_factor)
second_diagonal_value = B_factor*dt/(dx*dx) + A_factor*dt/(2*dx) # for x-1
third_diagonal_value = B_factor*dt/(dx*dx) - A_factor*dt/(2*dx) # for x+1

for i in range(0,x_interval-1):
    mbase[(i+1),i] = second_diagonal_value
    mbase[i,(i+1)] = third_diagonal_value

# Initial value for iteration process
# an inspired guess: we will say that u(x,0) behaves like a straight line
# that goes from the initial value to zero
initial_u = 250 - x_range*0.25
initial_t = 0
prev_u = initial_u
prev_t = initial_t

# Some graphical parameters, to keep plots consistent 
x_min = 0 
x_max = 300

for i in range(0,timesteps):
    current_time = prev_t + dt
    # --- boundary values must be defined for each timestep ---
    ib_u = initial_boundary(current_time) 
    fb_u = final_boundary(current_time)
    boundary_vector =  np.zeros(shape=(x_interval))
    boundary_vector[0] = second_diagonal_value*ib_u
    boundary_vector[len(boundary_vector)-1] = third_diagonal_value*fb_u
    # --- Linear System resolution ---
    ans = np.dot(mbase,prev_u) + boundary_vector
    prev_u = ans
    prev_t = current_time
    x = np.asarray(x_range)
    y = np.asarray(ans)
    tx = i % 5
    if (tx == 0):
        plt.plot(x,y)
        plt.ylim(x_min,x_max)
        plt.title('t='+str(np.round(current_time,3)))
        plt.show()
