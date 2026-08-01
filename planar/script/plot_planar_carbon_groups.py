from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


ROOT = Path('/Users/behnamazizi/Downloads/core level shifts/planar')
XYZ = ROOT / 'structure' / 'planar.xyz'
OUT = ROOT / 'figures' / 'Planar_carbon_groups'

GROUPS = {
    r'$C_{L,\alpha}$': [4, 5, 42, 43],
    r'$C_{\alpha}$': [20, 21, 26, 27],
    r'$C_{L,\beta}$': [2, 3, 44, 45],
    r'$C_{\beta}$': [22, 23, 24, 25],
    r'$C_M$': [6, 13, 28, 35],
    r'$C_b$': [14, 15, 16, 17, 18, 19, 29, 30, 31, 32, 33, 34],
    r'$C_w$': [7, 8, 9, 10, 11, 12, 36, 37, 38, 39, 40, 41],
}
COLORS = {
    r'$C_{L,\alpha}$': '#1565C0', r'$C_{\alpha}$': '#56B4E9',
    r'$C_{L,\beta}$': '#C62828', r'$C_{\beta}$': '#E76F9A',
    r'$C_M$': '#7B2CBF', r'$C_b$': '#2E7D32', r'$C_w$': '#E69F00',
}
CUTOFFS = {
    frozenset(('C','C')):1.78, frozenset(('C','N')):1.78,
    frozenset(('C','H')):1.25, frozenset(('Zn','N')):2.30,
}


def read_xyz(path):
    atoms=[]
    for index,line in enumerate(path.read_text().splitlines()[2:],start=1):
        fields=line.split()
        if len(fields)>=4:
            atoms.append((index,fields[0],np.array([float(v) for v in fields[1:4]])))
    return atoms


def group_for(index):
    for group,indices in GROUPS.items():
        if index in indices:
            return group
    return None


atoms=read_xyz(XYZ)
carbon_indices={i for i,e,_ in atoms if e=='C'}
assigned={i for values in GROUPS.values() for i in values}
assert carbon_indices==assigned,(carbon_indices-assigned,assigned-carbon_indices)

fig,ax=plt.subplots(figsize=(13.0,10.0),constrained_layout=True)
for i,(_,ei,ri) in enumerate(atoms):
    for j in range(i+1,len(atoms)):
        _,ej,rj=atoms[j]
        cutoff=CUTOFFS.get(frozenset((ei,ej)))
        if cutoff and np.linalg.norm(ri-rj)<=cutoff:
            ax.plot([ri[0],rj[0]],[ri[1],rj[1]],color='#8A8A8A',lw=1.55,zorder=1)

styles={'H':('#B7DDE2',42),'N':('#173F5F',180),'Zn':('#8AB17D',390)}
for idx,element,r in atoms:
    if element=='C':
        continue
    color,size=styles[element]
    ax.scatter(r[0],r[1],s=size,c=color,edgecolors='white',linewidths=1.0,zorder=3)
    if element in {'N','Zn'}:
        label='Zn' if element=='Zn' else f'N{idx}'
        ax.text(r[0],r[1],label,ha='center',va='center',color='white',fontsize=7.4 if element=='N' else 8.5,fontweight='bold',zorder=4)

for idx,element,r in atoms:
    if element!='C':
        continue
    group=group_for(idx)
    ax.scatter(r[0],r[1],s=250,c=COLORS[group],edgecolors='white',linewidths=1.25,zorder=5)
    ax.text(r[0],r[1],str(idx),ha='center',va='center',color='white',fontsize=7.5,fontweight='bold',zorder=6)

handles=[Line2D([0],[0],marker='o',linestyle='',markersize=9.5,markerfacecolor=COLORS[name],markeredgecolor='white',label=f'{name}: '+', '.join(map(str,indices))) for name,indices in GROUPS.items()]
legend=ax.legend(handles=handles,title='Carbon groups and XYZ atom indices',loc='upper left',bbox_to_anchor=(1.005,0.97),frameon=True,borderpad=0.8,labelspacing=0.8,fontsize=10,title_fontsize=11)
legend.get_frame().set_edgecolor('#D0D5DB')
legend.get_frame().set_linewidth(0.8)
ax.text(1.01,0.28,'Other atoms\nN: dark blue\nZn: green\nH: pale cyan',transform=ax.transAxes,ha='left',va='top',fontsize=10,bbox=dict(boxstyle='round,pad=0.6',facecolor='#F5F7F9',edgecolor='#D0D5DB'))
ax.set_title('Planar molecule: carbon-group assignment',fontsize=20,fontweight='bold',pad=14)
ax.set_aspect('equal')
ax.set_xlim(-9.1,9.1)
ax.set_ylim(-8.7,8.7)
ax.axis('off')
fig.savefig(OUT.with_suffix('.png'),dpi=300,bbox_inches='tight',facecolor='white')
fig.savefig(OUT.with_suffix('.pdf'),bbox_inches='tight',facecolor='white')
print(OUT.with_suffix('.png'))
