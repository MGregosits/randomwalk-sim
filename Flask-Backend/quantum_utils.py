import cirq
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
from scipy.stats import kde
import base64
import io
import imageio

def initial_state(number_qubits: int, is_y=False):
    yield cirq.X.on(cirq.GridQubit(0, 0))
    yield cirq.H.on(cirq.GridQubit(0, number_qubits))
    yield cirq.S.on(cirq.GridQubit(0, number_qubits))
    if (is_y):
        yield cirq.Z.on(cirq.GridQubit(0, number_qubits))

def walk_step(number_qubits: int):

    # "Flip" the coin vector

    yield cirq.H.on(cirq.GridQubit(0, number_qubits))

    # Implement the Addition Operator

    yield cirq.X.on(cirq.GridQubit(0, number_qubits))

    for i in range(number_qubits, 0, -1):

        controls = [cirq.GridQubit(0, v) for v in range(number_qubits, i-1, -1)]
        yield cirq.X.on(cirq.GridQubit(0, i-1)).controlled_by(*controls)
        if (i > 1):
            yield cirq.X.on(cirq.GridQubit(0, i-1))

    yield cirq.X.on(cirq.GridQubit(0, number_qubits))

    # Implement the Subtraction Operator

    for i in range(1, number_qubits+1):

        controls = [cirq.GridQubit(0, v) for v in range(number_qubits, i-1, -1)]
        yield cirq.X.on(cirq.GridQubit(0, i-1)).controlled_by(*controls)
        if (i < number_qubits):
            yield cirq.X.on(cirq.GridQubit(0, i))


def generate_walk(number_qubits: int, iterator: int, sample_number: int, is_y=False):
    qubits = cirq.GridQubit.rect(1, number_qubits)
    circuit = cirq.Circuit()
    circuit.append(initial_state(number_qubits, is_y))
    for j in range(iterator):
        circuit.append(walk_step(number_qubits))
    state_vector = cirq.final_state_vector(circuit)
    circuit.append(cirq.measure(*qubits, key='x'))
    #print(circuit)
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=sample_number)
    final = result.histogram(key='x')
    return final, state_vector


def state_vector_2_probability(state_vector):
    for index in range(0, state_vector.shape[0], 2):
        state_vector[index] = np.abs(state_vector[index])**2 + np.abs(state_vector[index + 1])**2
    state_vector = np.delete(state_vector, range(1, state_vector.shape[0], 2))

    df_state_vector = pd.DataFrame(state_vector, columns=["Probabilites"])
    #df_state_vector = df_state_vector.apply(lambda x: np.abs(x)**2)
    df_state_vector["Position_Vectors"] = df_state_vector.index

    for id, data in df_state_vector.iterrows():
        if (data["Probabilites"] == 0+0j):
            df_state_vector.drop(id, axis=0, inplace=True)
    df_state_vector.reset_index(drop=True ,inplace=True)

    return df_state_vector


def results_2_df(final, sample_number):

    x_arr = list(final.keys())
    y_arr = [dict(final)[j] for j in dict(final).keys()]

    x_arr_final = []
    y_arr_final = []

    while (len(x_arr) > 0):

        x_arr_final.append(min(x_arr))
        y_arr_final.append(y_arr[x_arr.index(min(x_arr))])
        holder = x_arr.index(min(x_arr))
        del x_arr[holder]
        del y_arr[holder]

    
    dict_final = dict(Position_Vectors=x_arr_final,Occurances=y_arr_final)
    data_final = pd.DataFrame.from_dict(dict_final, orient='columns')
    data_final = data_final.assign(Probabilites = lambda x: (x["Occurances"] / sample_number))
    #data_final = data_final.assign(Qubits = lambda x: (x['Qubits']%number_qubits))
    data_final

    return data_final


def bar_quantum(data_final):
    fig, ax = plt.subplots(figsize=(20,10))
    sns.barplot(data=data_final, x='Position_Vectors', y='Occurances', ax=ax)
    ax.bar_label(ax.containers[0], fontsize=1)
    ax.set_title("Count of steps on each node")
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return image_base64


def heatmap_quantum(data_final):
    fig, ax = plt.subplots(figsize=(20,10))
    nbins=256
    k = kde.gaussian_kde([data_final['Position_Vectors'],data_final['Occurances']])
    xi, yi = np.mgrid[data_final['Position_Vectors'].min():data_final['Position_Vectors'].max():nbins*1j, data_final['Occurances'].min():data_final['Occurances'].max():nbins*1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto')
    ax.set_title("Heatmap of the quantum walk")
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return image_base64


def increment_gate(circuit, qpos, qcoin):
    n = len(qpos)
    for i in range(n):
        controls = qcoin[:] + qpos[i+1:]
        circuit.append(cirq.X.on(qpos[i]).controlled_by(*controls))


def decrement_gate(circuit, qpos, qcoin):
    n = len(qpos)
    for i in range(n):
        if i + 1 < n:
            operations = []
            for j in range(i+1,n):
                operations.append(cirq.X(qpos[j]))
            moment = cirq.Moment(operations)
            circuit.append(moment)
        controls = qcoin[:] + qpos[i+1:]
        circuit.append(cirq.X.on(qpos[i]).controlled_by(*controls))
        if i + 1 < n:
            operations_2 = []
            for k in range(i+1,n):
                operations_2.append(cirq.X(qpos[k]))
            moment_2 = cirq.Moment(operations_2)
            circuit.append(moment_2)


def step(circuit, qpos, qcoin):
    coin_moment_h = [cirq.H(qcoin[0]), cirq.H(qcoin[1])]
    circuit.append(coin_moment_h)
    increment_gate(circuit, qpos[len(qpos)//2:], qcoin)
    circuit.append(cirq.X(qcoin[0]))
    decrement_gate(circuit, qpos[len(qpos)//2:], qcoin)
    coin_moment_x = [cirq.X(qcoin[0]), cirq.X(qcoin[1])]
    circuit.append(coin_moment_x)
    increment_gate(circuit, qpos[:len(qpos)//2], qcoin)
    circuit.append(cirq.X(qcoin[0]))
    decrement_gate(circuit, qpos[:len(qpos)//2], qcoin)

def initialize_2D(circuit, n ,pos, qpos):
    formatLabel = '{0:0' + str(n) + 'b}'
    x = formatLabel.format(pos[0])
    y = formatLabel.format(pos[1])
    for i in range(len(x)):
        if x[i] == '1':
            circuit.append(cirq.X(qpos[i]))
    for j in range(len(y)):
        if y[j] == '1':
            circuit.append(cirq.X(qpos[n + j]))
    return circuit

def run_2d_walk(n, steps, sample_number):
    simulator = cirq.Simulator()

    qpos = cirq.NamedQubit.range(2 * n, prefix='pos_')
    qcoin = cirq.NamedQubit.range(2, prefix='coin_')

    circuit = cirq.Circuit()
    circuit = initialize_2D(circuit, n, [2**(n-1), 2**(n-1)], qpos)

    for i in range(steps):
        step(circuit, qpos, qcoin)
    state_vector = cirq.final_state_vector(circuit)

    circuit.append(cirq.measure(*qpos, key='x'))
    result = simulator.run(circuit, repetitions=sample_number)
    final = result.histogram(key='x')
    return final, state_vector
    

def convert_2d_results_to_coordinates(final, n, sample_number):
    x_coords = []
    y_coords = []
    occurrences = []

    for state, count in final.items():
        # Convert the integer state to its binary representation, padded to 2n digits
        binary_state = format(state, f'0{2 * n}b')
        
        # Split the binary string into x and y components
        x_bin = binary_state[:n]
        y_bin = binary_state[n:]
        
        # Convert binary strings to integer coordinates
        x_coord = int(x_bin, 2)
        y_coord = int(y_bin, 2)
        
        x_coords.append(x_coord)
        y_coords.append(y_coord)
        occurrences.append(count)

    data = pd.DataFrame({
        'X Coordinate': x_coords,
        'Y Coordinate': y_coords,
        'Occurrences': occurrences
    })

    data['Probabilities'] = data['Occurrences'] / sample_number
    data["Coordinates"] = data["X Coordinate"].astype(str) + ", " + data["Y Coordinate"].astype(str)
    data = data.sort_values(by="Coordinates")

    return data


def bar_quantum_2d(data_final: pd.DataFrame) -> str:
    """
    Creates a bar plot of occurrences and saves it as a PNG file.

    Args:
        data_final (pd.DataFrame): DataFrame containing data for the bar plot.

    Returns:
        Literal["static/bar_plot.png"]: Path to the saved PNG file.
    """
    fig, ax = plt.subplots(figsize=(20,10))
    sns.barplot(data=data_final, x='Coordinates', y='Occurrences', ax=ax)
    ax.bar_label(ax.containers[0], fontsize=1)
    ax.set_title("Counts of walks ending on each node")
    # Save the plot as an in-memory buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Encode the image data in base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return image_base64
    #plt.show()

def heatmap_quantum_2d(data_final: pd.DataFrame) -> str:
    """
    Creates a heatmap of occurrences based on coordinates and saves it as a PNG file.

    Args:
        data_final (pd.DataFrame): DataFrame containing data for the heatmap.

    Returns:
        str: Path to the saved heatmap image.
    """
    # Pivot the DataFrame to create a heatmap
    heatmap_data = data_final.pivot(index="Y Coordinate", columns="X Coordinate", values="Occurrences")

    # Create the heatmap
    plt.figure(figsize=(12, 12))
    sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".0f", cbar=True)
    plt.title("Heatmap of Occurrences")
    plt.xlabel("X Coordinates")
    plt.ylabel("Y Coordinates")
    plt.ylim(0, int(heatmap_data.index.max()) + 1)
    # Save the plot as an in-memory buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Encode the image data in base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    #plt.show()
    # Return the path to the saved heatmap image
    return image_base64


def generate_heatmaps_base64(data_frames: list, number_qubits: int) -> list:
    """
    Generates a list of heatmaps from data frames, returning each image in base64 encoding.

    Args:
        data_frames (list): A list of pandas DataFrames, each containing data for a heatmap.

    Returns:
        list: A list of base64-encoded strings, each representing a heatmap image.
    """
    base64_images = []

    for data_final in data_frames:
        # Create a heatmap for each data frame and encode it in base64
        grid_size = 2**number_qubits
        heatmap_data = np.zeros((grid_size, grid_size))

        for _, row in data_final.iterrows():
            x = row['X Coordinate']
            y = row['Y Coordinate']
            heatmap_data[y, x] = row['Occurrences']
        
        plt.figure(figsize=(12, 12))
        sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".0f", cbar=True)
        plt.title("Heatmap of Occurrences")
        plt.xlabel("X Coordinates")
        plt.ylabel("Y Coordinates")

        # Save the plot to an in-memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Encode the image data in base64
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        base64_images.append(image_base64)

        plt.close()

    return base64_images


def create_base64_gif_from_heatmaps(data_frames: list, number_qubits: int, duration=0.5) -> str:
    """
    Creates an animated GIF from a list of data frames representing heatmaps and returns it in base64 format.

    Args:
        data_frames (list): A list of pandas DataFrames, each containing data for a heatmap.
        duration (float): Duration of each frame in the GIF.

    Returns:
        str: A base64-encoded string representing the animated GIF.
    """
    # Generate the heatmap images in base64 format
    images = generate_heatmaps_base64(data_frames, number_qubits)
    image_objects = [imageio.imread(io.BytesIO(base64.b64decode(img))) for img in images]

    # Create the animated GIF and save it to an in-memory buffer
    gif_buffer = io.BytesIO()
    imageio.mimsave(gif_buffer, image_objects, format='GIF', duration=duration)
    gif_buffer.seek(0)

    # Encode the GIF data in base64
    gif_base64 = base64.b64encode(gif_buffer.read()).decode('utf-8')

    return gif_base64

