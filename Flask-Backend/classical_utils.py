import base64
import io
import time
from typing import List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import pydtmc as dtmc
import seaborn as sns
import matplotlib.pyplot as plt
plt.switch_backend('agg')


def generate_markov_chain_matrix(grid_size: Tuple[int, int], teleport_prob: float = 0.15) -> np.ndarray:
    matrix_size = grid_size[0] * grid_size[1]
    matrix = np.zeros((matrix_size, matrix_size))
    transitions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

   
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            possible_transitions = sum(1 for dx, dy in transitions if 0 <= i + dx < grid_size[0] and 0 <= j + dy < grid_size[1])
            for dx, dy in transitions:
                if 0 <= i + dx < grid_size[0] and 0 <= j + dy < grid_size[1]:
                    matrix[i * grid_size[1] + j][(i + dx) * grid_size[1] + (j + dy)] = (1 - teleport_prob) / possible_transitions

    matrix += teleport_prob / matrix_size
    return matrix


def torus_transition_matrix(grid_size: tuple) -> np.ndarray:
  """
  This function creates a transition matrix for a random walk on a torus.

  Args:
      grid_size: A tuple representing the size of the torus grid (m, n).

  Returns:
      A numpy array representing the transition matrix.
  """
  matrix_size = grid_size[0] * grid_size[1]
  P = np.zeros((matrix_size, matrix_size))

  if (grid_size[0] == grid_size[1]):
     for i in range(matrix_size):
        x = i % grid_size[0]
        y = i // grid_size[1]
        neighbors = [(i + grid_size[0]) % matrix_size, # Upper
                     (i - grid_size[0]) % matrix_size, # Lower
                     y * grid_size[0] + (x - 1 + grid_size[0]) % grid_size[0], # Left
                     y * grid_size[0] + (x + 1) % grid_size[0]] # Right
        for neighbor in neighbors:
           P[i][neighbor] += 1/4


  elif (grid_size[0] != grid_size[1]):
      for i in range(matrix_size):

        # Define neighbors with proper wrapping for torus
        neighbors = [(i - grid_size[0]) % matrix_size, # Upper
                     (i + grid_size[0]) % matrix_size, # Lower
                     (i - grid_size[1]) % matrix_size, # Left
                     (i + grid_size[1]) % matrix_size] # Right

        for neighbor in neighbors:
            P[i][neighbor] += 1/4

  return P


def initialize_processing(grid_size: Tuple[int, int]) -> Tuple[List[str], np.ndarray, dtmc.MarkovChain]:
    trans = torus_transition_matrix(grid_size)
    states = [str(i) for i in range(grid_size[0] * grid_size[1])]
    initial_dist = generate_initial_distribution(grid_size)
    mc = dtmc.MarkovChain(trans, states)
    return states, initial_dist, mc


def convert_states_to_coordinates(walk: List[str], grid_size: Tuple[int, int]):
    """
    Converts the walk states to coordinates using the get_target_coordinate function.

    Args:
        walk (List[str]): List of walk states.
        grid_size (Tuple[int, int]): Size of the torus grid (m, n).

    Returns:
        Tuple[List[int], List[int]]: Two lists of integers representing x and y coordinates.
    """
    x_coords, y_coords = zip(*[map(int, get_target_coordinate(int(state), grid_size).split(", ")) for state in walk])
    return list(x_coords), list(y_coords)
    


def walk_step_by_step(
    mc: dtmc.MarkovChain,
    n: int,
    target_state: Tuple[int, int],
    grid_size: Tuple[int, int],
    states: List[str],
    search_enabled: bool = True,
) -> Tuple[List[str], Optional[int]]:
    """
  This function creates a walk on the torus, searching for the target state by default, runs for n steps instead if search is disabled. 

  Args:
      mc: MarkovChain object representing the torus.
      n: number of the steps in the walk
      target_state: The state in the walk that we want to reach.
      grid_size: A tuple representing the size of the torus grid (m, n).
      states: List of possible state indexes as strings
      search_enabled: Bool to set if want to search for a state or not.

  Returns:
      An array with the states visited by the walk in order and the hitting time of the target state.
    """
    walk = [generate_random_int(states[0], states[-1])]
    hitting_time = None
    target_index = get_target_index(target_state, grid_size)
    for i in range(0, n):
        current_state = walk[-1]
        if search_enabled:
            if search_enabled and str(current_state) == str(target_index):
                hitting_time = i
                break
        next_state = mc.next(current_state)
        walk.append(next_state)
    return walk, hitting_time


def simulate_multiple_walks(
    mc: dtmc.MarkovChain,
    n: int,
    n_sims: int,
    target_state: Tuple[int, int],
    grid_size: Tuple[int, int],
    states: List[str],
    search_enabled: bool = False,
) -> Tuple[List[List[str]], List[Optional[int]]]:
    """
  This function simulates multiple random walks on a torus and collects data.

  Args:
      mc (pydtmc.MarkovChain): The Markov chain object representing the random walk on a torus.
      n: number of the steps in the walk
      n_sims (int): The number of simulations to run.
      target_state (tuple): The state in the walk that we want to reach.
      grid_size: A tuple representing the size of the torus grid (m, n).
      states: List of possible state indexes as strings
      search_enabled: Bool to set if we want to search for a state or not.

  Returns:
      tuple: A tuple containing two elements:
          - list: A list of lists, where each inner list represents the states visited in a single simulation.
          - list: A list containing the hitting times (steps taken) to reach the target state for each simulation, 
                  or None if the target state was not reached within n steps.
  """
    all_walks = []
    hitting_times = []
    for _ in range(n_sims):
        walk, hitting_time = walk_step_by_step(mc,n,target_state,grid_size, states,search_enabled)
        all_walks.append(walk)
        hitting_times.append(hitting_time)
    return all_walks, hitting_times


def get_target_index(target_state: Tuple[int, int], grid_size: Tuple[int, int]) -> int:
  """
  This function calculates the index of the target state in the torus grid.

  Args:
      target_state (tuple): The state in the walk that we want to reach.
      grid_size: A tuple representing the size of the torus grid (m, n).

  Returns:
      int: The index of the target state.
  """
  if (grid_size[0] == grid_size[1]):
      target_index = target_state[1] * grid_size[1] + target_state[0]
  elif (grid_size[0] != grid_size[1]):
      if (grid_size[0] < grid_size[1]):
          target_index = (target_state[0] * grid_size[1] - target_state[1] * grid_size[0]) % (grid_size[0] * grid_size[1])
      elif (grid_size[0] > grid_size[1]):
          target_index = (target_state[1] * grid_size[0] - target_state[0] * grid_size[1]) % (grid_size[0] * grid_size[1])
  return target_index


def get_target_coordinate(target_state_index: int, grid_size: Tuple[int, int]) -> str:
    """
  This function calculates the coordinates of the target state in the torus grid.

  Args:
      target_state_index (int): The state in the walk that we want to reach.
      grid_size: A tuple representing the size of the torus grid (m, n).

  Returns:
      int: The coordinates of the target state.
  """
    if (grid_size[0] == grid_size[1]):
        x = target_state_index % grid_size[0]
        y = target_state_index // grid_size[1]
    elif (grid_size[0] != grid_size[1]):
        x = target_state_index % grid_size[0]
        y = target_state_index % grid_size[1]
    return f"{x}, {y}"


def assign_mixing_time(mc: dtmc.MarkovChain, initial_dist: np.ndarray) -> str:
    if mc.is_ergodic:
        mixing_time = mc.mixing_time(initial_dist)
        if mixing_time is None:
            mixing_time = "100+"
    else:
        mixing_time = "The Markov chain is not ergodic"
    return mixing_time


def analyze_walk_data(all_walks: List[List[int]], grid_size: Tuple[int, int], only_final_steps: bool = False) -> pd.DataFrame:
    """
    This function analyzes the walk data and creates a DataFrame containing unique states, their occurrences, and probabilities.

    Args:
        all_walks (list): A list of lists, where each inner list represents the states visited in a single simulation.
        n_sims (int): The number of simulations run.

    Returns:
        pandas.DataFrame: A DataFrame containing unique states, their occurrences, and probabilities.
    """
    selected_steps = [walk[-1] for walk in all_walks] if only_final_steps else [state for walk in all_walks for state in walk]
    total_steps = len(selected_steps)  # Total number of steps in all simulations
    state_counts = {}
    for state in selected_steps:
        state_counts[state] = state_counts.get(state, 0) + 1
    state_data = [
            {"State": state, "Occurrences": count, "Probability": count / total_steps}
            for state, count in state_counts.items()
        ]
    df_state_analysis = pd.DataFrame(state_data)
    df_state_analysis['State'] = pd.to_numeric(df_state_analysis['State'])
    df_state_analysis = df_state_analysis.sort_values(by='State').reset_index(drop=True)
    df_state_analysis['Coordinates'] = df_state_analysis['State'].apply(lambda x: get_target_coordinate(x, grid_size))
    return df_state_analysis


def compute_theoretical_distribution(states: List[str], transition_matrix: np.ndarray, grid_size: Tuple[int, int], steps: int) -> pd.DataFrame:
    step_transition_matrix = np.linalg.matrix_power(transition_matrix, steps)
    
    # Generate a normalized random initial distribution
    initial_distribution = generate_initial_distribution(grid_size)
    
    # Compute the distribution after the given number of steps
    distribution_after_steps = np.dot(initial_distribution, step_transition_matrix)
    
    # Ensure the resulting distribution is normalized
    distribution_after_steps /= distribution_after_steps.sum()
    
    distribution_df = pd.DataFrame({
        "State": states,
        "Probability": distribution_after_steps
    })
    distribution_df['State'] = pd.to_numeric(distribution_df['State'])
    distribution_df['Coordinates'] = distribution_df['State'].apply(lambda x: get_target_coordinate(x, grid_size))
    return distribution_df


def bar_plot_occurrences(data_final: pd.DataFrame) -> str:
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
    ax.set_title("Count of steps on each node")
    # Save the plot as an in-memory buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Encode the image data in base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return image_base64


def heatmap_occurrences(data_final: pd.DataFrame) -> str:
    """
    Creates a heatmap of occurrences based on coordinates and saves it as a PNG file.

    Args:
        data_final (pd.DataFrame): DataFrame containing data for the heatmap.

    Returns:
        str: Path to the saved heatmap image.
    """
    # Extract X and Y coordinates from the "Coordinates" column
    data_final[["X", "Y"]] = data_final["Coordinates"].str.split(", ", expand=True)

    # Pivot the DataFrame to create a heatmap
    heatmap_data = data_final.pivot(index="Y", columns="X", values="Occurrences")

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

    # Return the path to the saved heatmap image
    return image_base64


def generate_initial_distribution(grid_size: Tuple[int, int], initial_state: int=0, is_random: bool=True) -> np.ndarray:
    """
    Generate a random or predefined initial distribution for the grid.
    
    Args:
        grid_size: A tuple representing the size of the grid (m, n).
    
    Returns:
        A numpy array representing the initial distribution.
    """
    num_states = grid_size[0] * grid_size[1]
    if is_random:
        initial_dist = np.ones(num_states) / num_states
    elif not is_random:
        initial_dist = initial_dist = np.zeros((grid_size[0] * grid_size[1]))
        initial_dist[initial_state] = 1
    return initial_dist



def generate_random_int(min_val: Union[int, str], max_val: Union[int, str]) -> str:
    """
    Generates a random integer between min_val and max_val (inclusive) based on system clock.

    Args:
        min_val (int): Minimum value.
        max_val (int): Maximum value.

    Returns:
        str: Random integer as a string.
    """
    min_val = int(min_val)
    max_val = int(max_val)

    # Get the current timestamp
    timestamp = int(time.time() * 1000)

    # Calculate the range of possible values
    range_val = max_val - min_val + 1

    # Generate a random integer based on the timestamp
    random_int = (timestamp % range_val) + min_val

    # Return the random integer as a string
    return str(random_int)