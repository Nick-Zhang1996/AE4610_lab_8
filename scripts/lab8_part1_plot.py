import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

data = np.load('lab8_log.npy')
t = data[:,0]
x = data[:,1]
y = data[:,2]
z = data[:,3]
tx = data[:,4]
ty = data[:,5]
tz = data[:,6]

fig = plt.figure()
ax = fig.add_subplot(3,1,1)
ax.plot(x,color='r', label='x actual')
ax.plot(tx,'--',color='b', label='x target')
ax.legend()

ax = fig.add_subplot(3,1,2)
ax.plot(y,color='r', label='y actual')
ax.plot(ty,'--',color='b', label='y target')
ax.legend()

ax = fig.add_subplot(3,1,3)
ax.plot(z,color='r', label='z actual')
ax.plot(tz,'--',color='b', label='z target')
ax.legend()

plt.show()

# Plot 3d trajectory
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot(x,y,z, color='r', label='actual')
ax.plot(tx,ty,tz,'--', color='b', label='target')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('altitude (z)')
ax.legend()
plt.show()

