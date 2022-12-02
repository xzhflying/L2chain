from turtle import color
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker

font = {
    'size':40
}
mpl.rc('font', **font)
plt.rcParams['ytick.direction'] = 'in'
n = 3
x = np.arange(n)+1

QR=[14493, 55, 45]
CAP=[17237, 756, 610]
L2R=[16837, 1401, 1212]
QP=[14023, 30.1, 19.4]
SP=[14123, 121, 111]
L2P=[16837, 257, 227]

# for i in range(len(L2R)):
#     L2R[i] = int(L2R[i]/1.8)

# for i in range(len(L2R)):
#     CAP[i] = int(CAP[i]/1.2)

# Set the title and the labels of x-axis and y-axis
# plt.xlabel('k', fontsize=40)
text=plt.ylabel('Throughput (tps)', fontsize=40)

fig = plt.gcf()
fig.set_size_inches(12, 7)

ax = plt.gca()
ax.spines['top'].set_linewidth(3)
ax.spines['right'].set_linewidth(3)
ax.spines['left'].set_linewidth(3)
ax.spines['bottom'].set_linewidth(3)
ax.yaxis.set_major_locator(ticker.MultipleLocator(300.0))
# ax.set_ylim([0, 19000])

ax.tick_params("y", which='major', length=15, width= 2)

plt.rcParams['hatch.color'] = 'w'
plt.rcParams['hatch.linewidth'] = 3
plt.yscale('log')

bar_label_size = 26

b1 = plt.bar(x - 0.36, QR, width=0.115, label=r'Quorum-R', color = 'w', edgecolor='#95a2ff', hatch = '/', lw='3')
b2 = plt.bar(x - 0.22, CAP, width=0.115, label=r'CAPER', color = '#fa8080', edgecolor='#fa8080', lw='3')
b3 = plt.bar(x - 0.07, L2R, width=0.115, label=r'L2chain-R', color = 'w', edgecolor='#ffc076', hatch = '/', lw='3')
b4 = plt.bar(x + 0.07, QP, width=0.115, label=r'Quorum-P', color = '#fae768', edgecolor='#fae768', lw='3')
b5 = plt.bar(x + 0.22, SP, width=0.115, label=r'Slim-P', color = 'w', edgecolor='#87e885', hatch = '/', lw='3')
b6 = plt.bar(x + 0.36, L2P, width=0.115, label=r'L2chain-P', color = '#3cb9fc', edgecolor='#3cb9fc', hatch = '/', lw='3')

group_labels = [r'read-only',r'read-write',r'write-only']
plt.xticks(x, group_labels, rotation=0)
leg=ax.legend(prop={'size': 30}, bbox_to_anchor=(-0.09, 1.03, 1, 0.2), ncol = 3, loc='center', borderaxespad=0, frameon=False)
# plt.show()

plt.text(x = 1 - 0.39, y = .01 * QR[0], s = "{:.1f}k".format(QR[0]/1000), ha='center', fontsize = bar_label_size)
plt.text(x = 1 - 0.23, y = .1 * CAP[0], s = "{:.1f}k".format(CAP[0]/1000), ha='center', fontsize = bar_label_size)
plt.text(x = 1 - 0.07, y = .5 * L2R[0], s = "{:.1f}k".format(L2R[0]/1000), ha='center', fontsize = bar_label_size)
plt.text(x = 1 + 0.09, y = .01 * QP[0], s = "{:.1f}k".format(QP[0]/1000), ha='center', fontsize = bar_label_size)
plt.text(x = 1 + 0.25, y = .1 * SP[0], s = "{:.1f}k".format(SP[0]/1000), ha='center', fontsize = bar_label_size)
plt.text(x = 1 + 0.39, y = .5 * L2P[0], s = "{:.1f}k".format(L2P[0]/1000), ha='center', fontsize = bar_label_size)


for x in [2, 3]:
    plt.text(x = x - 0.36, y = 1.05 * QR[x-1], s = str(QR[x-1]), ha='center', fontsize = bar_label_size)
    plt.text(x = x - 0.22, y = 1.05 * CAP[x-1], s = str(CAP[x-1]), ha='center', fontsize = bar_label_size)
    plt.text(x = x - 0.07, y = 1.05 * L2R[x-1], s = str(L2R[x-1]), ha='center', fontsize = bar_label_size)
    plt.text(x = x + 0.07, y = 1.05 * QP[x-1], s = str(QP[x-1]), ha='center', fontsize = bar_label_size)
    plt.text(x = x + 0.22, y = 1.05 * SP[x-1], s = str(SP[x-1]), ha='center', fontsize = bar_label_size)
    plt.text(x = x + 0.36, y = 1.05 * L2P[x-1], s = str(L2P[x-1]), ha='center', fontsize = bar_label_size)


plt.savefig('../../../workload_tps.pdf',
            bbox_extra_artists=(leg,text),
            bbox_inches='tight')