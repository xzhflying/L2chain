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

QR_break = [[0, 
14.7 - 0.13 - 0.33 - 0.1, 
16.7 - 0.18 - 0.32 - 0.1], 
[0.04, 0.13, 0.18], [0.34, 0.33, 0.32]]
CAP_break = [[0, 
1.9 - 0.11 - 0.1, 
2.3 - 0.1 - 0.1], 
[0.09, 0.11, 0.1], [0, 0, 0]]
L2R_break = [[0, 
5.6 - 0.21 - 3.1 - 0.1, 
5.9 - 0.26 - 3.7 - 0.1], 
[0.14, 0.21, 0.26], [0.35, 3.1, 3.7]]
QP_break = [[0, 
10.7 - 0.13 - 0.33 - 0.1, 
11.4 - 0.18 - 0.32 - 0.1], 
[0.05, 0.13, 0.18], [0.35, 0.33, 0.32]]
SP_break = [[0, 
10.1, 
10.3], 
[0.1, 0.11, 0.15], [0.35, 0.2, 0.3]]
L2P_break = [[0, 
13.7 - 0.25 - 3.2 - 0.1, 
14.8 - 0.29 - 3.9 - 0.1], 
[0.15, 0.25, 0.29], [0.36, 3.2, 3.9]]

QR=[0.4, 14.7, 16.7]
CAP=[0.1, 1.9, 2.3]
L2R=[0.5, 5.6, 5.9]
QP=[0.4, 10.7, 11.4]
SP=[0.5, 10.1 + 0.2 + 0.11, 10.3 + 0.3 + 0.15]
L2P=[0.5, 13.7, 14.8]

# Set the title and the labels of x-axis and y-axis
# plt.xlabel('k', fontsize=40)
text=plt.ylabel('Latency (s)', fontsize=40)

fig = plt.gcf()
fig.set_size_inches(13.5, 6)

ax = plt.gca()
ax.spines['top'].set_linewidth(3)
ax.spines['right'].set_linewidth(3)
ax.spines['left'].set_linewidth(3)
ax.spines['bottom'].set_linewidth(3)
ax.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
ax.set_ylim([0, 23])

ax.tick_params("y", which='major', length=15, width= 2)

# plt.rcParams['hatch.color'] = 'w'
# plt.rcParams['hatch.linewidth'] = 3

bar_label_size = 20

b1 = plt.bar(x - 0.36, QR, width=0.115, label=r'Quorum-R', color = 'w' , edgecolor='#95a2ff', lw='5')
# ax.bar_label(b1, fontsize = bar_label_size)
b2 = plt.bar(x - 0.22, CAP, width=0.115, label=r'CAPER', color = 'w', edgecolor='#fa8080', lw='5')
# ax.bar_label(b2, fontsize = bar_label_size)
b3 = plt.bar(x - 0.07, L2R, width=0.115, label=r'L2chain-R', color = 'w', edgecolor='#ffc076', lw='5')
# ax.bar_label(b3, fontsize = bar_label_size)
b4 = plt.bar(x + 0.07, QP, width=0.115, label=r'Quorum-P', color = 'w', edgecolor='#fae768', lw='5')
# ax.bar_label(b4, fontsize = bar_label_size)
b5 = plt.bar(x + 0.22, SP, width=0.115, label=r'Slim-P', color = 'w', edgecolor='#87e885', lw='5')
# ax.bar_label(b5, fontsize = bar_label_size)
b6 = plt.bar(x + 0.36, L2P, width=0.115, label=r'L2chain-P', color = 'w', edgecolor='#3cb9fc', lw='5')
# ax.bar_label(b6, fontsize = bar_label_size)

plt.bar(x - 0.36, QR_break[0], width=0.08, label=r'Consensus', 
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x - 0.36, QR_break[1], width=0.08, label=r'Execution',
        bottom=QR_break[0], hatch='x', edgecolor='#A149FA', color='w',lw='1')
plt.bar(x - 0.36, QR_break[2], width=0.08, label=r'Overhead',
        bottom=np.array(QR_break[0]) + np.array(QR_break[1]), 
        hatch='.', edgecolor='#FF06B7', color='w',lw='1')

plt.bar(x - 0.22, CAP_break[0], width=0.08, 
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x - 0.22, CAP_break[1], width=0.08,
        bottom=CAP_break[0], hatch='x', edgecolor='#A149FA', color='w',lw='1')
plt.bar(x - 0.22, CAP_break[2], width=0.08,
        bottom=np.array(CAP_break[0]) + np.array(CAP_break[1]), hatch='.', edgecolor='#FF06B7', color='w',lw='1')

plt.bar(x - 0.07, L2R_break[0], width=0.08,
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x - 0.07, L2R_break[1], width=0.08,
        bottom=L2R_break[0], hatch='x', edgecolor='#A149FA', color='w',lw='1')
plt.bar(x - 0.07, L2R_break[2], width=0.08,
        bottom=np.array(L2R_break[0]) + np.array(L2R_break[1]), hatch='.', edgecolor='#FF06B7', color='w',lw='1')

plt.bar(x + 0.07, QP_break[0], width=0.08,
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x + 0.07, QP_break[1], width=0.08,
        bottom=QP_break[0], hatch='x', edgecolor='#A149FA', color='w',lw='1')
plt.bar(x + 0.07, QP_break[2], width=0.08,
        bottom=np.array(QP_break[0]) + np.array(QP_break[1]), hatch='.', edgecolor='#FF06B7', color='w',lw='1')

plt.bar(x + 0.22, SP_break[0], width=0.08,
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x + 0.22, SP_break[1], width=0.08,
        bottom=SP_break[0], hatch='x', edgecolor='#A149FA', color='w',lw='1')
plt.bar(x + 0.22, SP_break[2], width=0.08,
        bottom=np.array(SP_break[0]) + np.array(SP_break[1]), hatch='.', edgecolor='#FF06B7', color='w',lw='1')

plt.bar(x + 0.36, L2P_break[0], width=0.08,
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x + 0.36, L2P_break[1], width=0.08,
        bottom=L2P_break[0], hatch='x', edgecolor='#A149FA', color='w',lw='1')
plt.bar(x + 0.36, L2P_break[2], width=0.08,
        bottom=np.array(L2P_break[0]) + np.array(L2P_break[1]), hatch='.', edgecolor='#FF06B7', color='w',lw='1')

group_labels = [r'read-only',r'read-write',r'write-only']
plt.xticks(x, group_labels, rotation=0)
leg=ax.legend(prop={'size': 30}, bbox_to_anchor=(-0.07, 1.15, 1, 0.2), ncol = 3, loc='center', borderaxespad=0, frameon=False)
# plt.show()

for x in np.arange(n)+1:
        plt.text(x = x - 0.36, y = 1.05 * QR[x-1], s = "{:.1f}".format(QR[x-1]), ha='center', fontsize = bar_label_size)
        plt.text(x = x - 0.22, y = 1.05 * CAP[x-1], s = "{:.1f}".format(CAP[x-1]), ha='center', fontsize = bar_label_size)
        plt.text(x = x - 0.07, y = 1.05 * L2R[x-1], s = "{:.1f}".format(L2R[x-1]), ha='center', fontsize = bar_label_size)
        plt.text(x = x + 0.07, y = 1.13 * QP[x-1], s = "{:.1f}".format(QP[x-1]), ha='center', fontsize = bar_label_size)
        plt.text(x = x + 0.22, y = 1.05 * SP[x-1], s = "{:.1f}".format(SP[x-1]), ha='center', fontsize = bar_label_size)
        plt.text(x = x + 0.36, y = 1.05 * L2P[x-1], s = "{:.1f}".format(L2P[x-1]), ha='center', fontsize = bar_label_size)

plt.savefig('../../../workload_latency.pdf',
            bbox_extra_artists=(leg,text),
            bbox_inches='tight')