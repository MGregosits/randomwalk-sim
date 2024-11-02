from flask import Flask, request
from flask_cors import CORS
from classical_utils import *
from quantum_utils import *

app = Flask(__name__)
CORS(app)

@app.route('/classical_1d', methods=['POST'])
def classical_1d():
    data = request.get_json()
    n = data.get('n')
    n_states = data.get('n_states')
    n_sims = data.get('n_sims')

    trans = circular_1d_transition_matrix(n_states)
    states = [str(i) for i in range(n_states)]
    mc = dtmc.MarkovChain(trans, states)

    all_walks = simulate_multiple_walks_1d(mc, n, n_sims, n_states, states)

    df_state_analysis = analyze_walk_data_1d(all_walks, n_states, only_final_steps=True)

    bar_plot_1d_base64 = bar_plot_1d(df_state_analysis)
    heatmap_1d_base64 = heatmap_1d(df_state_analysis)

    result = {"bar_plot_1d": bar_plot_1d_base64, "heat_map_1d": heatmap_1d_base64}
    return result

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    n = data.get('n')
    grid_size = (data.get('grid_x'), data.get('grid_y'))
    target_state = (data.get('target_x'), data.get('target_y'))

    states, initial_dist, mc = initialize_processing(grid_size)

    walk, hitting_time = walk_step_by_step(mc, n, target_state, grid_size, states, True)

    x, y = convert_states_to_coordinates(walk, grid_size)

    mixing_time = assign_mixing_time(mc, initial_dist)

    # Convert the x and y arrays to lists and return as a JSON object
    result = {'x': x, 'y': y, 'walk': walk, 'grid_x': grid_size[0],
              'grid_y': grid_size[1], 'hitting_time': hitting_time, 'mixing_time': mixing_time}
    return result


@app.route('/multiple_runs', methods=['POST'])
def multiple_runs():
    data = request.get_json()
    n = data.get('n')
    grid_size = (data.get('grid_x'), data.get('grid_y'))
    target_state = (data.get('target_x'), data.get('target_y'))
    n_sims = data.get('n_sims')

    states, initial_dist, mc = initialize_processing(grid_size)

    # Simulate multiple walks
    all_walks, hitting_times = simulate_multiple_walks(mc, n, n_sims, target_state, grid_size, states, False)

    # Analyze walk data
    df_state_analysis = analyze_walk_data(all_walks, grid_size, only_final_steps=True)

    # Create a plots of occurrences
    bar_plot_base64 = bar_plot_occurrences(df_state_analysis)
    heatmap_base64 = heatmap_occurrences(df_state_analysis)

    result = {"bar_plot": bar_plot_base64, "heat_map": heatmap_base64}
    return result


@app.route('/quantum', methods=['POST'])
def quantum():
    data = request.get_json()
    number_qubits = data.get('number_qubits')
    iterator = data.get('iterator')
    sample_number = data.get('sample_number')

    final, state_vector = generate_walk(number_qubits, iterator, sample_number)

    data_final = results_2_df(final, sample_number)

    barplot_base64 = bar_quantum(data_final)

    heatmap_base64 = heatmap_quantum(data_final)

    # Convert the x and y arrays to lists and return as a JSON object
    result = {'bar_plot_q': barplot_base64, 'heatmap_q': heatmap_base64}
    return result


@app.route('/quantum_2d', methods=['POST'])
def quantum_2d():
    data = request.get_json()
    number_qubits = data.get('number_qubits')
    iterator = data.get('iterator')
    sample_number = data.get('sample_number')

    final, state_vector = run_2d_walk(number_qubits, iterator, sample_number)

    data_final = convert_2d_results_to_coordinates(final, number_qubits, sample_number)

    barplot_base64 = bar_quantum_2d(data_final)

    heatmap_base64 = heatmap_quantum_2d(data_final)

    list_for_gif_heatmap = []

    for i in range(1, iterator + 1):
        f_iter, sv_iter = run_2d_walk(number_qubits, i, sample_number)
        df_iter = convert_2d_results_to_coordinates(f_iter, number_qubits, sample_number)
        list_for_gif_heatmap.append(df_iter)

    heatmap_gif_base64 = create_base64_gif_from_heatmaps(list_for_gif_heatmap, number_qubits)

    # Convert the x and y arrays to lists and return as a JSON object
    result = {'bar_plot_q_2d': barplot_base64, 'heatmap_q_2d': heatmap_base64, 'heatmap_q_2d_gif': heatmap_gif_base64}
    return result


if __name__ == '__main__':
    app.run(debug=True)