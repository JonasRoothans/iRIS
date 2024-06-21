import numpy as np
from classes.vote import Vote
from classes.member import Member
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
import matplotlib.colors as mcolors
import os
from scipy.spatial.distance import cosine
from functions.plotPCA import plot_pca_scatter


# get all vote ids
files = os.listdir('json/votes')
ids = []
i = 0
for f in files:
    ids.append(int(f[0:-5]))
ids = sorted(ids)

# --init
member_legend = {}
member_names = []
conclusion = {}
dates = {}
v_index = 0
n_members = 46
n_votes = len(files)
data = np.ndarray([n_members, n_votes])
data[:] = None

#Create a custom colormap
cdict = {
    'red':   [(0.0, 1.0, 1.0),
              (0.5, 1.0, 1.0),
              (1.0, 0.0, 0.0)],

    'green': [(0.0, 0.0, 0.0),
              (0.5, 1.0, 1.0),
              (1.0, 1.0, 1.0)],

    'blue':  [(0.0, 0.0, 0.0),
              (0.5, 0.0, 0.0),
              (1.0, 0.0, 0.0)]
}
custom_cmap = mcolors.LinearSegmentedColormap('CustomMap', segmentdata=cdict, N=256)



for iFile, id in enumerate(ids):
    v = Vote(id)

    #Only this cycle
    if v.date < "2022-04-01":
        continue

    if v.result == 'aangenomen':
        conclusion[v_index] = True
    else:
        conclusion[v_index] = False

    #Assign an index to the member id, because the set of members per vote is inconsistent
    for member in v.member_votes:
        if member in member_legend:
            i = member_legend[member]
        else:
            i = len(member_legend)
            member_legend[member] = i
            member_names.append(Member(member).name)



        print(f'i:{i}, iFile:{iFile}')
        if v.member_votes[member] == 'voor':
            data[i, v_index] = 1
        elif v.member_votes[member] == 'afwezig':
            data[i, v_index] = None
        else:
            data[i, v_index] = -1

        dates[v_index] = v.date

    #Next vote
    v_index += 1


#Extract chronology
data = data[0:len(member_legend)-1,0:v_index]
chronology = [k for k, v in sorted(dates.items(), key=lambda p: p[1], reverse=False)]

#Sort according to chronology
sorted = data[:,chronology[:]]


#result
sorted_conclusion = []
for key in chronology:
    if key in conclusion:
        sorted_conclusion.append(1 if conclusion[key] else -1)

#sort members
def calculate_similarity(row,reference):
    # Combine both and filter out NaNs
    valid_mask = ~np.isnan(row)
    valid_row = row[valid_mask]
    valid_reference = reference[valid_mask]


    if len(valid_row)==0:
        return 0 # if all elements were NaN, return 0 similarity

    # Calculate the number of matching elements
    matching_elements = np.sum(valid_row == valid_reference)

    # Calculate percentage similarity
    similarity_percentage = (matching_elements / len(valid_row)) * 100
    return similarity_percentage

similarities = []
for row in sorted:
    similarity = calculate_similarity(row,np.array(sorted_conclusion))
    similarities.append(similarity)

# Create pairs of similarity scores and rows
similarity_row_member_pairs = list(zip(similarities, sorted,member_names))

# Sort these pairs based on the similarity scores in descending order
similarity_row_member_pairs.sort(key=lambda x: x[0], reverse=True)

# Extract the rows and member names in sorted order
sorted_data = np.array([row for _, row, _ in similarity_row_member_pairs])
sorted_member_names = [f'{name} ({similarity:.0f}%)' for similarity, _, name in similarity_row_member_pairs]

# Prepend the conclusion_vector to the sorted_data
sorted_data = np.vstack((sorted_conclusion, sorted_data))
# Prepend 'conclusion' to the sorted_member_names
sorted_member_names.insert(0, 'conclusion')

#--- visualisation
# Calculate appropriate figure size to make cells cubic
rows, cols = sorted_data.shape
cell_size = 1  # Each cell will be 1 inch by 1 inch

fig_width = cols * cell_size
fig_height = rows * cell_size

# Create the figure with calculated size
fig, ax1 = plt.subplots(figsize=(5,5))

# Plot using imshow
cax = ax1.imshow(sorted_data, aspect='auto', interpolation='none', cmap=custom_cmap)



# Define the y-tick positions and labels
y_ticks = np.arange(len(member_legend)+1)
y_tick_labels = [f' {i}' for i in sorted_member_names]

# Set the y-tick positions and labels
plt.yticks(ticks=y_ticks, labels=y_tick_labels)




# Display the plot
plt.show()


#plot_similarity_matrix(sorted_data,sorted_member_names)
plot_pca_scatter(sorted_data,sorted_member_names)