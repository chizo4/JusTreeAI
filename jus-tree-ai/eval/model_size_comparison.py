'''
--------------------------------------------------------------
FILE:
    jus-tree-ai/eval/model_size_comparison.py

INFO:
    Plot the model size comparison: Memory v Param sizes.

AUTHOR:
    @chizo4 (Filip J. Cierkosz)

VERSION:
    01/2025
--------------------------------------------------------------
'''

import matplotlib.pyplot as plt

# Model configs.
models = ['LLaMA 3.2', 'Qwen 2.5', 'DeepSeek-R1']
parameters = [3.2, 1.5, 8.0]  # (B)
memory = [2.0, 1.0, 4.7]  # (GB)

# Set up the bubble size.
bubble_sizes = [param * 500 for param in parameters]
# Colors.
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

# Create the plot.
plt.figure(figsize=(8, 6))
plt.scatter(parameters, memory, s=bubble_sizes, c=colors, alpha=0.6, edgecolors='k')
for i, model in enumerate(models):
    plt.text(
        parameters[i] + 0.05,
        memory[i] + 0.05,
        f'{model}\n({parameters[i]}B, {memory[i]}GB)',
        fontsize=14,
        ha='left',
        va='center',
        fontweight='bold'
    )
# Labels etc.
plt.xlabel('Parameters (B)', fontsize=18, fontweight='bold')
plt.ylabel('Memory Usage (GB)', fontsize=18, fontweight='bold')
plt.title('Model Size vs Memory Usage', fontsize=22, fontweight='bold')
# Axis adjustments.
plt.xticks([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], fontsize=14)
plt.yticks([0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0], fontsize=14)
plt.grid(True, linestyle='--', alpha=0.6)

# Save the plot as PNG.
plt.savefig('resources/plots/model_size_vs_memory_updated.png', dpi=300)
plt.show()
