import matplotlib.pyplot as plt
import numpy as np

# Data from https://allisonhorst.github.io/palmerpenguins/
species = ("Objective Evaluation", "Self-Assessment", "Peer Review")
penguin_means = {
    'Amount of Information Received': (4.33, 5.00, 5.00),
    'Goal Completion': (5.00, 5.00, 5.00),
    'Role Consistency': (4.56, 4.67, 4.67),
    'Humanity, Interest, Curiosity, Participation': (4.00, 4.67, 4.67),
    'Risk and Issue Prediction': (3.00, 3.00, 3.00),
}

x = np.arange(len(species))  # the label locations
width = 0.1  # the width of the bars (slightly narrower)
spacing = 0.05  # space between the groups of bars
multiplier = 0

# Create the figure and axis objects
fig, ax = plt.subplots(figsize=(8, 6), layout='constrained')

# Loop through the attributes and plot them
for attribute, measurement in penguin_means.items():
    offset = (width + spacing) * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3, fontsize=10)
    multiplier += 1

# Add some text for labels, title, and custom x-axis tick labels
ax.set_ylabel('Evaluation Score (1-5)', fontsize=12)
ax.set_title('Low-Difficulty Scenarios', fontsize=14)
ax.set_xticks(x + (width * (len(penguin_means) - 1) + spacing * (len(penguin_means) - 1)) / 2, labels=species)
ax.legend(loc='upper left', ncols=3, fontsize=10)
ax.set_ylim(1, 6)

# Improve gridlines and style
ax.grid(True, axis='y', linestyle='--', alpha=0.7)
ax.set_facecolor('#f4f4f4')

# Display the plot
plt.show()
