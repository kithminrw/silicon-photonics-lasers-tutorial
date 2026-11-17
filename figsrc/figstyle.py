"""figstyle.py -- matplotlib house style for the Open-Photonics figures.

    from figstyle import *
    fig, ax = plt.subplots(figsize=FULL)
    ax.plot(x, y, color=C1)
    finish(ax, xlabel="Wavelength (µm)", ylabel="Index")
    savefig(fig, "ch02_dispersion")      # -> assets/figs/ch02_dispersion.svg

SVG text stays as text (svg.fonttype = none), so the browser draws it in the page's sans-serif font.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, TEAL, BLUE, AMBER, RED, VIOLET, MUTED, GRID = "#172036", "#0B7A85", "#2556B8", "#C98A1C", "#B5473A", "#6B5CA5", "#57647A", "#E1E6EF"
C1, C2, C3, C4, C5, C6 = BLUE, AMBER, TEAL, RED, VIOLET, INK
SERIES = [C1, C2, C3, C4, C5, C6]
FULL, FULLTALL, HALF = (6.3, 2.7), (6.3, 3.6), (3.05, 2.4)
FIGDIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs"))

plt.rcParams.update({
    "svg.fonttype": "none", "font.family": "sans-serif",
    "font.sans-serif": ["Libre Franklin", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5, "legend.fontsize": 7.5,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.linewidth": 0.8, "lines.linewidth": 1.6,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 100, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04, "savefig.transparent": True, "axes.axisbelow": True,
})


def finish(ax, xlabel=None, ylabel=None, title=None, legend=False, loc="best"):
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if title: ax.set_title(title, loc="left", color=INK, fontweight="bold")
    if legend: ax.legend(loc=loc)


def tag(ax, s):
    """Panel letter in the top-left corner."""
    ax.text(-0.02, 1.06, s, transform=ax.transAxes, fontweight="bold", color=INK, fontsize=9.5, ha="right")


def savefig(fig, name):
    os.makedirs(FIGDIR, exist_ok=True)
    path = os.path.join(FIGDIR, name + ".svg")
    fig.savefig(path, metadata={"Date": None})
    plt.close(fig)
    print("wrote", path)
