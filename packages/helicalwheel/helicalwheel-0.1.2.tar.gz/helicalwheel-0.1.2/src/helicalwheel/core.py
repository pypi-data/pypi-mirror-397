#%% Preliminaries: Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import math
from pathlib import Path

#%% Defining Amino Acid Classes and Colors
"""
AA classification is based on: 
Bongioanni A, Bueno MS, Mezzano BA, Longhi MR, Garnero C. Amino acids and its pharmaceutical applications: A mini review. Int J Pharm. 2022 Feb 5;613:121375. doi: 10.1016/j.ijpharm.2021.121375. Epub 2021 Dec 11. PMID: 34906648.
"""

# Classfiy the AAs
class_dic = {
     "Positive": ['D', 'E'],
     "Negative": ['H', 'K', 'R'],
     "Aromatic": ['F', 'W', 'Y'],
     "S-containing": ['C', 'M'],
     "Hydrophilic": ['N', 'Q', 'S', 'T'],
     "Hydrophobic": ["A", "I", "L", "V", "G"],
     "Special": ["P"]
     }

# Assign colors to each class
color_dic = {
    "Positive": "#9467bd",  
    "Negative": "#6b8eef",  
    "Aromatic": "#70d270",   
    "S-containing": "#58564f",   
    "Hydrophilic": "#f7dd58", 
    "Hydrophobic": "#C04949",
    "Special":  "#F491FB" 
}

# Create a dictionary mapping each AA to its class and color
aa_dic = {}
for key in class_dic:
    for aa in class_dic[key]:
        aa_dic[aa] = {"class": key, "color": color_dic[key]}


#%% Helix coordinates function


def helix_coordinates(sequence, radius=1.0, angle_per_residue=100, rotate_deg=0):       

    """
    Parameters:
    - sequence: string of amino acid sequence
    - radius: float, radius of the helix (default: 1.0)
    - angle_per_residue: float, angle between consecutive residues in degrees (default: 100) (typical for alpha-helix)
    - rotate_deg: float, rotation angle of the entire helix in degrees (counter-clockwise, default: 0)
    """

    seq = sequence.upper() # convert to uppercase
    n = len(seq)

    # Check for invalid AAs
    invalid = set([aa for aa in sequence.upper() if aa not in aa_dic])
    if invalid:
        raise ValueError(f"Invalid amino acid one letter code in sequence: {invalid}")

    # Calculate angles in radians
    angle_step = np.deg2rad(angle_per_residue) # angle between residues in radians
    angles = -np.arange(n) * angle_step - np.deg2rad(-90)  # Start at top (−90°)

    # Rotate if specified
    if rotate_deg:
        rotate = np.deg2rad(rotate_deg) # rotate the entire helix by this angle in degrees, counter-clockwise
        angles += rotate
        print(f"Rotating helix by {rotate_deg} degrees (counter-clockwise)!")

    # Calculate x and y coordinates from angles
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)


    df = pd.DataFrame({
        "index": np.arange(n),
        "residue": list(seq),
        "angle_rad": angles,
        "x": x,
        "y": y
    })
    return df

# %% Plotting function

def helixplot(df, makebold=None, subtitle=True, legend=True, first_pos=0):

    """
    Parameters:
    - makebold: bool, if True, mutated residues (if "mutated" column exists) will be shown in bold font
    - subtitle: bool, if not stated otherwise, each wheel will have a subtitle indicating the residue range
    - legend: bool, if not stated otherwise, a legend will be added to the plot 
    - first_pos: int, position number of the first residue in the sequence (for subtitle purposes)
    """

# Index reset
    df = df.reset_index(drop=True)  # Reset the index (for sliced panda frames)

# Check if df has "mutated" column
    boldletters = True if "mutated" in df.columns and makebold else False


# Testing the AA sequence
    max_n = 18 # maximum number of residues per wheel
    min_n = 2  # minimum number of residues to plot a wheel

    if len(df) < min_n:
        print(f"Sequence too short to plot a helical wheel (min. {min_n} residues required).")

    # Divide DataFrame into chunks of max_n residues
    chunks = [group for bin, group in df.groupby(df.index // max_n)]
    n_chunks = len(chunks)

    if len(chunks) > 1:
        print(f"Sequence length exceeds {max_n} residues. Dividing into {n_chunks} wheels.")


    #  Plot
    cols = math.ceil(math.sqrt(n_chunks))   # number of columns
    rows = math.ceil(n_chunks / cols)       # number of rows
    fig, axes = plt.subplots(rows, cols, figsize=(cols*5, rows*5,))

    if isinstance(axes, plt.Axes):      # 1x1 case
        axes = np.array([axes])
    else:
        axes = axes.flatten()
    

    for ax in axes:
        ax.axis("off")
        ax.margins(0.1)  

    count = 0 # to keep track of how many lines have been drawn
    lw_seq = np.linspace(6, 3, len(df)-n_chunks) / 1.6  # line width for connecting lines based on sequence length
    lw_seq = np.flip(lw_seq)  # reverse the sequence so that the first lines are thicker

    for i, chunk in enumerate(chunks):
        x1, y1 = chunk["x"].values[:-1], chunk["y"].values[:-1]
        x2, y2 = chunk["x"].values[1:], chunk["y"].values[1:]
        
        for j in reversed(range(0, len(chunk)-1)):
            lw = lw_seq[count]
            count +=1
            axes[i].plot(
                [x1[j], x2[j]], [y1[j], y2[j]], color="#555555", linewidth=lw, zorder=0,
                # adding a white halo effect to the lines for better visibility
                path_effects=[
                    pe.Stroke(linewidth=lw + 3, foreground="white"),
                    pe.Normal()
                            ]
                         )

        aa = chunk["residue"]
        x = chunk["x"].values
        y = chunk["y"].values
        col = [aa_dic[a]["color"] for a in aa]

        # Add circles
        axes[i].scatter(x, y, color=col, s=1200)   

        # Add letters
        for j, a in enumerate(aa):
                  axes[i].text(x[j], y[j], a, ha="center", va="center", 
                        fontsize=15,
                        fontweight= "bold" if boldletters and chunk.iloc[j]["mutated"] else "normal")
        if subtitle == True:
            axes[i].set_title(f"Residues {chunk.iloc[0]['index']+first_pos}-{chunk.iloc[-1]['index']+first_pos} ")


    # Add figure legend
    if legend == True:
        legend_handles = [mpatches.Patch(color=color, label=category) 
                    for category, color in color_dic.items()]
        
        bbooxy = 1.3 - (cols-1) * 0.12  # adjust bbox_to_anchor x-position based on number of columns
        
        fig.legend(
            handles=legend_handles,
            loc='center right',
            bbox_to_anchor=(bbooxy, 0.5),
            title="Residue Categories",
            #title_fontweight='bold'  # make the title bold
        )
