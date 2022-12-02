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

L2R_break=[[8.41, 4.63, 2.26, 1.12],
[6.03, 2.93, 1.41, 0.74]]
L2P_break=[[11.48, 5.34, 2.60, 1.41],
[6.32, 3.01, 1.45, 0.88]]
L2R_tps = [405, 711, 1390, 2530]
L2P_tps = [66, 136, 247, 438]

L2R = []
L2P = []
for i in range(n):
    L2R.append(L2R_break[0][i] + L2R_break[1][i] + 0.1)
    L2P.append(L2P_break[0][i] + L2P_break[1][i] + 0.1)


# Set the title and the labels of x-axis and y-axis
# plt.xlabel('k', fontsize=40)
# text=plt.ylabel('Overhead (s)', fontsize=40)
fig = plt.figure()
# set the figure size ratio
fig.set_size_inches(12, 7)

# do not show the top-right line
ax1 = fig.add_subplot(111)

text1 = ax1.set_ylabel('Overhead (s)', fontsize=40)

# ax = plt.gca()
ax1.spines['top'].set_linewidth(3)
ax1.spines['right'].set_linewidth(3)
ax1.spines['left'].set_linewidth(3)
ax1.spines['bottom'].set_linewidth(3)
ax1.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
ax1.set_ylim([0, 20])
ax1.tick_params("y", which='major', length=15, width= 2)

plt.rcParams['hatch.color'] = 'w'
plt.rcParams['hatch.linewidth'] = 3

bar_label_size = 26

b1 = plt.bar(x - 0.22, L2R, width=0.4, label=r'L2chain-R', color = 'w', edgecolor='#1F6CC0', lw=3)
ax1.bar_label(b1, fontsize = bar_label_size)
b2 = plt.bar(x + 0.22, L2P,  width=0.4, label=r'L2chain-P', color = 'w', edgecolor='#FDBF50', lw=3)
ax1.bar_label(b2, fontsize = bar_label_size)
plt.bar(x - 0.22, L2R_break[0], width=0.35, label=r'Wit-upd', 
        hatch='//', edgecolor='pink', color='w',lw='1')
plt.bar(x - 0.22, L2R_break[1], width=0.35, label=r'Wit-gen',
        bottom = L2R_break[0], hatch='x', edgecolor='g', color='w',lw='1')
plt.bar(x + 0.22, L2P_break[0], width=0.35, 
        hatch='//', edgecolor='pink', color='w',lw='1')
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
ax2.yaxis.set_major_locator(ticker.MultipleLocator(600.0))
ax2.set_ylim([0, 2600])
ax2.tick_params("y", which='major', length=15, width= 2)


l1 = plt.plot(x, L2R_tps, label=r'L2chain-R-tps', linewidth=2, marker='^', markersize=16, color='r')
l2 = plt.plot(x, L2P_tps, label=r'L2chain-P-tps', linewidth=2, marker='o', markersize=16, color='#8A2BE2')
leg2 = ax2.legend(prop={'size': 30}, frameon = False, columnspacing=1.2,
					  bbox_to_anchor=(1.1, 1.3), borderaxespad=0)

group_labels = [r'$4$',r'$8$',r'$16$',r'$32$']
plt.xticks(x, group_labels, rotation=0)
# leg=ax.legend(prop={'size': 30}, bbox_to_anchor=(-0.09, 1.03, 1, 0.2), ncol = 3, loc='center', borderaxespad=0, frameon=False)
# plt.show()

plt.savefig('../../../thread.pdf',
            bbox_extra_artists=(leg1, leg2, text1, text2),
            bbox_inches='tight')