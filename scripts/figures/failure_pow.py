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

QP_break=[[9.7, 9.9, 9.8, 10.1],
[0.29 + 0.13, 0.26 + 0.12, 0.27 + 0.13, 0.3 + 0.15]]
L2P_break=[[9.5, 10.1, 10.9, 13.8],
[3.9 + 0.17, 3.8 + 0.16, 3.6 + 0.2, 3.9 + 0.19]]
QP_tps = [29.9, 29.3, 29.5, 29.1]
L2P_tps = [246, 241, 238, 198]

QP = []
L2P = []
for i in range(n):
    QP.append(QP_break[0][i] + QP_break[1][i] + 0.1)
    L2P.append(L2P_break[0][i] + L2P_break[1][i] + 0.1)

# for i in range(len(L2R)):
#     L2R[i] = int(L2R[i]/1.8)

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

b1 = plt.bar(x - 0.22, QP, width=0.4, label=r'Quorum-P', color = 'w', edgecolor='#ff6600', lw=5)
ax1.bar_label(b1, fontsize = bar_label_size)
b2 = plt.bar(x + 0.22, L2P,  width=0.4, label=r'L2chain-P', color = 'w', edgecolor='#3cb9fc', lw=5)
ax1.bar_label(b2, fontsize = bar_label_size)
plt.bar(x - 0.22, QP_break[0], width=0.35, label=r'Consensus', 
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x - 0.22, QP_break[1], width=0.35, label=r'Exe+Over',
        bottom = QP_break[0], hatch='x', edgecolor='g', color='w',lw='1')
plt.bar(x + 0.22, L2P_break[0], width=0.35, 
        hatch='//', edgecolor='cyan', color='w',lw='1')
plt.bar(x + 0.22, L2P_break[1], width=0.35,
        bottom = L2P_break[0], hatch='x', edgecolor='g', color='w',lw='1')

leg1 = ax1.legend(prop={'size': 30}, frameon = False, columnspacing=1.2, ncol = 2,
		bbox_to_anchor=(0.6, 1.3), borderaxespad=0)


ax2=ax1.twinx()
text2 = ax2.set_ylabel('Throughput (tps)', fontsize=40)
ax2.spines['top'].set_linewidth(3)
ax2.spines['right'].set_linewidth(3)
ax2.spines['left'].set_linewidth(3)
ax2.spines['bottom'].set_linewidth(3)
ax2.yaxis.set_major_locator(ticker.MultipleLocator(50.0))
ax2.set_ylim([0, 260])
ax2.tick_params("y", which='major', length=15, width= 2)


l1 = plt.plot(x, QP_tps, label=r'Quorum-P-tps', linewidth=2, marker='^', markersize=16, color='#ff6600')
l2 = plt.plot(x, L2P_tps, label=r'L2chain-P-tps', linewidth=2, marker='o', markersize=16, color='#3cb9fc')
leg2 = ax2.legend(prop={'size': 30}, frameon = False, columnspacing=1.2,
					  bbox_to_anchor=(1.1, 1.3), borderaxespad=0)

group_labels = [r'$0\%$',r'$10\%$',r'$20\%$',r'$30\%$']
plt.xticks(x, group_labels, rotation=0)
# leg=ax.legend(prop={'size': 30}, bbox_to_anchor=(-0.09, 1.03, 1, 0.2), ncol = 3, loc='center', borderaxespad=0, frameon=False)
# plt.show()

plt.savefig('../../../failure_pow.pdf',
            bbox_extra_artists=(leg1, leg2, text1, text2),
            bbox_inches='tight')