import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Function to read the data from the file
def read_points_from_file(filename):
    x_vals, y_vals, z_vals = [], [], []
    
    # Open the file and read each line
    with open(filename, 'r') as file:
        for line in file:
            # Split the line by commas and convert to floats
            x, y, z = map(float, line.strip().split(','))
            x_vals.append(x)
            y_vals.append(y)
            z_vals.append(z)
    
    return x_vals, y_vals, z_vals

# Function to plot the 3D path
def plot_3d_path(x_vals, y_vals, z_vals):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Plotting the path as a line plot
    ax.plot(x_vals, y_vals, z_vals, label='Snake Path', color='b')

    # Add red dots at each point
    ax.scatter(x_vals, y_vals, z_vals, color='r', s=3)  # s=50 for dot size
    
    # Add labels and title
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_title('3D Path of Points')

    # Show the plot
    plt.show()

# Main function to read the file and plot the points
def plot_snake_of_pathfile(filename):

    # Read the points from the file
    x_vals, y_vals, z_vals = read_points_from_file(filename)
    
    # Plot the points in 3D
    plot_3d_path(x_vals, y_vals, z_vals)