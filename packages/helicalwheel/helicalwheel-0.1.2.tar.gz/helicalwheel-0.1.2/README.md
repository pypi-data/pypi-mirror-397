# helicalwheel: Helical Wheel Representation of Alpha-Helices

## Description

Creates a two-dimensional top-down view of an alpha-helix sequence. The advantages of this package are:
* Easy rotations of the diagram are possible
* Sequences longer than 18 amino acids are split into multiple diagrams and plotted next to each other
* Easy readibility due to increasing line thickness connecting the AA corresponding to their position in the helix
* Alternative helices (e.g. 3<sub>10</sub>) can be drawn by adjusting the input angle

**Important**: This package does **not** predict whether a peptide sequence will form an alpha helix. The graph only visualizes the arrangement of residues **assuming** an alpha helix is present. We recommend first using AlphaFold or other structure prediction tools, and then using this package to visualize the predicted alpha helices.

Built by Jann Staebler, PhD student (Institute of Virology, University of Zurich)

## Dependencies

* NumPy
* Pandas
* Matplotlib

## Installation

The source code can be found on GitHub: https://github.com/jastaeb/helicalwheel

Python package index at: https://pypi.org/project/helicalwheel/

Helicalwheel can be installed as follows:
```python
python -m pip install -U pip
python -m pip install -U helicalwheel
```

## Usage

```python   
#%% Load helixvis
import helicalwheel as hw

#%% Input sequence
# Section of a predicted alpha helix of the assembly-activating protein of Adenovirus-associated virus serotype 2
aap2_seq = "LVWELIRWLQAVAHQWQTIT" 

# Creating a dataframe with helix coordinates
df_wt=hw.helix_coordinates(aap2_seq)

#%% Plotting
first_pos=21 # indicate the first alpha-helix residue position in the total protein sequence

# Entire helix
wt_plot_1 = hw.helixplot(df_wt, first_pos=first_pos)
# Two individual plots figure assembly
wt_plot_1 = hw.helixplot(df_wt.iloc[0:10], legend=False, first_pos=first_pos)
wt_plot_2 = hw.helixplot(df_wt.iloc[10:], legend=False, first_pos=first_pos)
```


## License
MIT
