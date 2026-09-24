"""Generate editable learning diagrams for chapters 11--13, not research results.

Run from any directory: python scripts/generate_heat_learning_figures.py
Each figure has a PNG for MyST and an SVG for editing.
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'assets' / 'figures' / 'learning'
plt.rcParams.update({'font.size': 11, 'svg.fonttype': 'none', 'savefig.dpi': 160})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for extension in ['png', 'svg']:
        fig.savefig(OUT / f'{name}.{extension}', bbox_inches='tight')
    plt.close(fig)


def variable_width_balance():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), layout='constrained')
    y = np.linspace(0, 1, 201)
    a = .7-.45*y
    ax = axes[0]
    ax.fill_betweenx(y, -a/2, a/2, facecolor='#d4e8f4', edgecolor='#356c8d')
    for yy in np.arange(.15, 1, .15):
        half = (.7-.45*yy)/2
        ax.plot([-half, half], [yy, yy], color='#6a93aa', lw=1)
    ax.plot([-.35, .35], [0, 0], color='firebrick', lw=4)
    yy = .45
    half = (.7-.45*yy)/2
    ax.annotate('', (half, yy), (-half, yy), arrowprops={'arrowstyle': '<->'})
    ax.text(0, yy+.025, r'$a(\xi)$', ha='center')
    ax.set(xlim=(-.55, .55), ylim=(-.06, 1.08), xlabel=r'width $\widehat{x}$',
           ylabel=r'height $\xi$', title='Width changes the conducting section')
    ax.set_aspect('equal')
    ax = axes[1]
    ax.add_patch(Rectangle((.3, .35), .4, .3, fc='#d4e8f4', ec='#356c8d', lw=2))
    ax.annotate('', (.5, .35), (.5, .1), arrowprops={'arrowstyle': '->', 'lw': 3, 'color': 'firebrick'})
    ax.annotate('', (.5, .9), (.5, .65), arrowprops={'arrowstyle': '->', 'lw': 3, 'color': 'firebrick'})
    ax.text(.53, .18, r'$\widehat{F}(\xi)$', color='firebrick')
    ax.text(.53, .83, r'$\widehat{F}(\xi+d\xi)$', color='firebrick')
    ax.annotate('', (.97, .5), (.7, .5), arrowprops={'arrowstyle': '->', 'lw': 2, 'color': 'tab:blue'})
    ax.text(.79, .57, 'loss from\nboth faces', color='tab:blue', ha='center')
    ax.text(.5, .5, r'$a(\xi)\,d\xi$', ha='center', va='center')
    ax.annotate('', (.25, .35), (.25, .65), arrowprops={'arrowstyle': '<->'})
    ax.text(.23, .5, r'$d\xi$', ha='right', va='center')
    ax.text(.5, -.035, 'incoming heat = outgoing heat + face loss', ha='center')
    ax.set(xlim=(0, 1.1), ylim=(-.1, 1.03), title='Balance on one height interval')
    ax.axis('off')
    save(fig, '11_variable_width_balance')


def base_condition_choices():
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), layout='constrained')
    titles = ['Full heated base', 'Partial heating + insulation', 'Partial heating + convection']
    for i, ax in enumerate(axes):
        ax.add_patch(Rectangle((-.5, 0), 1, 1.15, fc='#e0eef6', ec='0.4', lw=2))
        heat = .5 if i == 0 else .18
        ax.plot([-heat, heat], [0, 0], color='firebrick', lw=5, solid_capstyle='butt')
        ax.text(0, .11, r'$U=1$', ha='center', color='firebrick')
        if i == 1:
            ax.plot([-.5, -.18], [0, 0], color='0.4', lw=4)
            ax.plot([.18, .5], [0, 0], color='0.4', lw=4)
            ax.text(0, -.17, r'unheated part: $\partial_n U=0$', ha='center')
        elif i == 2:
            for x in [-.4, -.28, .28, .4]:
                ax.annotate('', (x, -.22), (x, -.01), arrowprops={'arrowstyle': '->', 'color': 'tab:blue', 'lw': 1.5})
            ax.text(0, -.34, 'unheated part: Robin condition', ha='center', color='tab:blue')
        else:
            ax.text(0, -.17, 'heated width = entire base width', ha='center')
        ax.text(0, .68, 'face convection\nremains active', ha='center', color='#356c8d')
        ax.set(xlim=(-.73, .73), ylim=(-.4, 1.3), title=titles[i], aspect='equal')
        ax.axis('off')
    save(fig, '12_base_condition_choices')


def cut_cell_geometry():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.9), layout='constrained')
    ax = axes[0]
    d, n = .25, 6
    x = (np.arange(n)+.5)*d
    inside = x[:, None]+x[None, :] < 1.5
    for j in range(n):
        for i in range(n):
            if inside[j, i]:
                ax.add_patch(Rectangle((i*d, j*d), d, d, fc='#d4e8f4', ec='none'))
                for di, dj in [(1, 0), (0, 1)]:
                    ni, nj = i+di, j+dj
                    if ni >= n or nj >= n or not inside[nj, ni]:
                        if di:
                            ax.plot([(i+1)*d]*2, [j*d, (j+1)*d], color='tab:blue', lw=3)
                        else:
                            ax.plot([i*d, (i+1)*d], [(j+1)*d]*2, color='tab:blue', lw=3)
    for e in np.arange(n+1)*d:
        ax.axhline(e, color='.8', lw=.6, zorder=0)
        ax.axvline(e, color='.8', lw=.6, zorder=0)
    ax.plot([0, 1.5], [1.5, 0], color='black', lw=2, label='true oblique boundary')
    ax.plot([], [], color='tab:blue', lw=3, label='staircase boundary')
    ax.legend(loc='upper right', fontsize=9)
    ax.set(xlim=(-.05, 1.6), ylim=(-.05, 1.6), aspect='equal', title='Area and perimeter are different tests')
    ax = axes[1]
    ax.add_patch(Rectangle((0, 0), 1, 1, fc='white', ec='.45', lw=2))
    ax.add_patch(Polygon([(0, 0), (1, 0), (1, .4), (.4, 1), (0, 1)], fc='#d4e8f4', ec='none'))
    ax.plot([1, .4], [.4, 1], color='black', lw=2)
    ax.plot([1, 1], [0, .4], color='tab:orange', lw=5)
    ax.plot(.5, .5, 'o', color='tab:blue')
    ax.text(.25, .28, r'$\phi_i=0.82$', ha='center')
    ax.text(.82, .83, r'$\ell_i=0.6\sqrt{2}$', rotation=-45, ha='center')
    ax.text(1.05, .2, r'$a_f=0.4$', va='center')
    ax.text(.5, -.13, r'$d_x=1$', ha='center')
    ax.text(-.12, .5, r'$d_y=1$', rotation=90, va='center')
    ax.text(.5, 1.17, r'cut line: $x+y=1.4$', ha='center')
    ax.set(xlim=(-.25, 1.43), ylim=(-.22, 1.32), title='One cut cell: three geometric quantities', aspect='equal')
    ax.axis('off')
    save(fig, '12_cut_cell_geometry')


def shape_comparison_design():
    y = np.linspace(0, 1, 401)
    area, contact = .5, .12
    profiles = [area*(1-.5+1*y), area*np.ones_like(y), area*(1+.5-1*y),
                contact*(1-y)+(area-contact/2)*np.pi/2*np.sin(np.pi*y)]
    titles = ['s = -0.5', 's = 0', 's = 0.5', 'curved profile']
    fig, axes = plt.subplots(2, 4, figsize=(10, 6.8), sharex=True, sharey=True, layout='constrained')
    for row in range(2):
        for col, a in enumerate(profiles):
            ax = axes[row, col]
            ax.fill_betweenx(y, -a/2, a/2, fc='#d4e8f4', ec='#356c8d', lw=1.5)
            hw = a[0]/2 if row == 0 else contact/2
            ax.plot([-hw, hw], [0, 0], color='firebrick', lw=4, solid_capstyle='butt')
            ax.set_title(titles[col], fontsize=11)
            ax.set(xlim=(-.45, .45), ylim=(-.07, 1.05), aspect='equal')
            if col == 0:
                ax.set_ylabel(('A: full base' if row == 0 else 'B: common contact')+'\nheight')
            if row == 1:
                ax.set_xlabel('width')
    fig.suptitle('Equal planform area: 0.5; red = heated interval; other edges insulated')
    save(fig, '13_shape_comparison_design')


if __name__ == '__main__':
    variable_width_balance()
    base_condition_choices()
    cut_cell_geometry()
    shape_comparison_design()
    print(f'Saved 4 PNG + 4 editable SVG diagrams to {OUT}')
