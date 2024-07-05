from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def plot_pca_scatter(sorted_data, sorted_member_names):
    if len(sorted_data) > 35:
        names = []
        for name in sorted_member_names:
            x = name.split()
            names.append(x[0])
    else:
        names = sorted_member_names

    # Perform PCA on the data
    pca = PCA(n_components=3)
    principal_components = pca.fit_transform(sorted_data)
    print(pca.explained_variance_ratio_)

    # Plot the PCA results with labels
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, label in enumerate(names):
        ax.scatter(principal_components[i, 0], principal_components[i, 1])
        ax.text(principal_components[i, 0], principal_components[i, 1],label, fontsize=9)

    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.set_title('PCA of Sorted Data')

    plt.tight_layout()
    plt.show()