import numpy as np
import matplotlib.pyplot as plt


def plot_similarity_matrix(sorted_data, sorted_member_names):
    names = []
    for name in sorted_member_names:
        x = name.split()
        names.append(x[0])

    # Number of rows
    num_rows = sorted_data.shape[0]

    # Initialize the similarity matrix
    similarity_matrix = np.zeros((num_rows, num_rows))

    # Calculate similarity as percentage of matching elements (ignoring NaNs)
    def calculate_similarity_percentage(row1, row2):
        valid_mask = ~np.isnan(row1) & ~np.isnan(row2)
        valid_row1 = row1[valid_mask]
        valid_row2 = row2[valid_mask]

        if len(valid_row1) == 0:
            return 0  # If all shared elements are NaN, return 0% similarity

        matching_elements = np.sum(valid_row1 == valid_row2)
        similarity_percentage = (matching_elements / len(valid_row1)) * 100
        return similarity_percentage

    # Fill the similarity matrix
    for i in range(num_rows):
        for j in range(num_rows):
            similarity_matrix[i, j] = calculate_similarity_percentage(sorted_data[i], sorted_data[j])

    # Plot the similarity matrix
    fig, ax1 = plt.subplots()
    cax = ax1.imshow(similarity_matrix, aspect='auto', interpolation='none', cmap='coolwarm', vmin=0, vmax=100)

    # Set y-axis labels and x-axis labels
    ax1.set_yticks(np.arange(num_rows))
    ax1.set_yticklabels(names, rotation=0)
    ax1.set_xticks(np.arange(num_rows))
    ax1.set_xticklabels(names, rotation=90)

    # Add colorbar to the plot
    cbar = fig.colorbar(cax, ax=ax1, orientation='vertical')
    cbar.set_label('Similarity (%)')


    # Display the plot
    plt.show()