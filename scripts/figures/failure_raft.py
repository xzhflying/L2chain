from re import L
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
n = 4
x = np.arange(n)+1

QR_break=[[16.28, 16.8, 17.9, 19.3],
[0.31 + 0.11, 0.33 + 0.1, 0.29 + 0.13, 0.3 + 0.15]]
L2R_break=[[1.64, 2.3, 3.2, 5.3],
[3.9 + 0.23, 3.8 + 0.21, 4.1 + 0.23, 3.9 + 0.22]]
QR_tps = [52, 51, 48, 42]
L2R_tps = [2504, 2428, 2153, 1652]

QP = []
L2P = []
for i in range(n):
    QP.append(QR_break[0][i] + QR_break[1][i] + 0.1)
    L2P.append(L2R_break[0][i] + L2R_break[1][i] + 0.1)

for i in range(len(L2R_tps)):
    L2R_tps[i] = int(L2R_tps[i]/1.8)

# Set the title and the labels of x-axis and y-axis
# plt.xlabel('k', fontsize=40)
# text=plt.ylabel('Overhead (s)', fontsize=40)
fig = plt.figure()
# set the figure size ratio
fig.set_size_inches(12, 7)

# do not show the top-right line
ax1 = fig.add_subplot(111)

text1 = ax1.set_ylabel('Latency (s)', fontsize=40)

# ax = plt.gca()
ax1.spines['top'].set_linewidth(3)
ax1.spines['right'].set_linewidth(3)
ax1.spines['left'].set_linewidth(3)
ax1.spines['bottom'].set_linewidth(3)
ax1.yaxis.set_major_locator(ticker.MultipleLocator(10.0))
ax1.set_ylim([0, 30])
ax1.tick_params("y", which='major', length=15, width= 2)

plt.rcParams['hatch.color'] = 'w'
plt.rcParams['hatch.linewidth'] = 3

bar_label_size = 26

b1 = plt.bar(x - 0.22, QP, width=0.4, label=r'Quorum-R', color = 'w', edgecolor='#95a2ff', lw=5)
ax1.bar_label(b1, fontsize = bar_label_size)
b2 = plt.bar(x + 0.22, L2P,  width=0.4, label=r'L2chain-R', color = 'w', edgecolor='#ffc076', lw=5)
ax1.bar_label(b2, fontsize = bar_label_size)
plt.bar(x - 0.22, QR_break[0], width=0.35, label=r'Consensus', 
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x - 0.22, QR_break[1], width=0.35, label=r'Exe+Over',
        bottom = QR_break[0], hatch='x', edgecolor='g', color='w',lw='1')
plt.bar(x + 0.22, L2R_break[0], width=0.35, 
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x + 0.22, L2R_break[1], width=0.35,
        bottom = L2R_break[0], hatch='x', edgecolor='g', color='w',lw='1')

leg1 = ax1.legend(prop={'size': 30}, frameon = False, columnspacing=1.2, ncol = 2,
		bbox_to_anchor=(0.6, 1.3), borderaxespad=0)


ax2=ax1.twinx()
text2 = ax2.set_ylabel('Throughput (tps)', fontsize=40)
ax2.spines['top'].set_linewidth(3)
ax2.spines['right'].set_linewidth(3)
ax2.spines['left'].set_linewidth(3)
ax2.spines['bottom'].set_linewidth(3)
ax2.yaxis.set_major_locator(ticker.MultipleLocator(300.0))
ax2.set_ylim([0, 1500])
ax2.tick_params("y", which='major', length=15, width= 2)


l1 = plt.plot(x, QR_tps, label=r'Quorum-R-tps', linewidth=2, marker='^', markersize=16, color='#95a2ff')
l2 = plt.plot(x, L2R_tps, label=r'L2chain-R-tps', linewidth=2, marker='o', markersize=16, color='#ffc076')
leg2 = ax2.legend(prop={'size': 30}, frameon = False, columnspacing=1.2,
					  bbox_to_anchor=(1.1, 1.3), borderaxespad=0)

group_labels = [r'$0\%$',r'$10\%$',r'$20\%$',r'$30\%$']
plt.xticks(x, group_labels, rotation=0)
# leg=ax.legend(prop={'size': 30}, bbox_to_anchor=(-0.09, 1.03, 1, 0.2), ncol = 3, loc='center', borderaxespad=0, frameon=False)
# plt.show()

plt.savefig('../../../failure_raft.pdf',
            bbox_extra_artists=(leg1, leg2, text1, text2),
            bbox_inches='tight')