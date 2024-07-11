from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def plot_pca_scatter(sorted_data, sorted_member_names,fig_title):
    if len(sorted_data) > 35:
        names = []
        for name in sorted_member_names:
            x = name.split()
            names.append(x[0])
    else:
        names = sorted_member_names

    # Perform PCA on the data
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(sorted_data)
    print(pca.explained_variance_ratio_)

    # Plot the PCA results with labels
    fig, ax = plt.subplots(figsize=(5,5))

    for i, label in enumerate(names):
        ax.scatter(principal_components[i, 0], principal_components[i, 1])
        ax.text(principal_components[i, 0], principal_components[i, 1],label, fontsize=9)

    ax.set_xlabel(f'Component 1 (verklaart {pca.explained_variance_ratio_[0]:.0%} variance)')
    ax.set_ylabel(f'Component 2 (verklaart {pca.explained_variance_ratio_[1]:.0%} variance)')
    # Turn off tick labels
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_title(fig_title)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    #plt.tight_layout()
    plt.show()