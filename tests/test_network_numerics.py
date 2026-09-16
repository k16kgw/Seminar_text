"""Check linear-system claims, graph orientation, and executable answer functions."""

import ast
from pathlib import Path

import nbformat
import networkx as nx
import numpy as np
import pytest
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]


def load_definitions(name, cell_ids):
    cells = {c.id: c for c in nbformat.read(ROOT / 'notebooks' / name, 4).cells}
    namespace = {}
    for cell_id in cell_ids:
        nodes = [n for n in ast.parse(cells[cell_id].source).body
                 if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), name, 'exec'), namespace)
    return namespace


@pytest.fixture(scope='module')
def linear():
    return load_definitions('41_love_dynamics_two_person.ipynb', ['imports', 'linear-tools'])


@pytest.fixture(scope='module')
def answers41():
    return load_definitions('solutions/41_love_dynamics_two_person_solutions.ipynb',
                            ['imports', 'linear-tools', 'classification-function', 'solution-functions'])


@pytest.fixture(scope='module')
def network():
    return load_definitions('solutions/42_love_dynamics_network_solutions.ipynb',
                            ['imports', 'linear-tools', 'network-tools', 'solution-functions'])


def test_solver_definitions_match_in_all_four_notebooks():
    sources = []
    for name in ['41_love_dynamics_two_person.ipynb', '42_love_dynamics_network.ipynb',
                 'solutions/41_love_dynamics_two_person_solutions.ipynb',
                 'solutions/42_love_dynamics_network_solutions.ipynb']:
        nb = nbformat.read(ROOT / 'notebooks' / name, 4)
        sources.append(next(c.source for c in nb.cells if c.id == 'linear-tools'))
    assert len(set(sources)) == 1


@pytest.mark.parametrize('stem', ['41_love_dynamics_two_person', '42_love_dynamics_network'])
def test_answer_notebook_repeats_current_exercises_and_has_executable_code(stem):
    main = nbformat.read(ROOT / 'notebooks' / (stem + '.ipynb'), 4)
    solution = nbformat.read(ROOT / 'notebooks' / 'solutions' / (stem + '_solutions.ipynb'), 4)
    prompt = next(c.source for c in main.cells if c.id == 'exercise')
    assert prompt in [c.source for c in solution.cells if c.cell_type == 'markdown']
    assert sum(c.cell_type == 'code' for c in solution.cells) >= 5


@pytest.mark.parametrize('matrix, label', [
    (np.diag([-1., -2.]), 'stable node'),
    ([[-1., 6.], [0., -1.]], 'stable node'),
    ([[-.2, 1.], [-1., -.2]], 'stable focus'),
    (np.diag([1., -1.]), 'saddle'),
    (np.diag([1., 2.]), 'unstable'),
])
def test_hyperbolic_classification(answers41, matrix, label):
    result = answers41['classify_linear_system'](matrix)
    assert result['classification'] == label
    np.testing.assert_allclose(result['trace'], sum(np.linalg.eigvals(matrix)))
    np.testing.assert_allclose(result['det'], np.prod(np.linalg.eigvals(matrix)))


@pytest.mark.parametrize('matrix', [
    [[0., 1.], [-1., 0.]], [[0., 1.], [0., 0.]], np.diag([0., -1.]),
    [[1e-12, 1.], [-1., 1e-12]],
])
def test_boundary_is_not_automatically_classified_as_stable(answers41, matrix):
    assert answers41['classify_linear_system'](matrix)['stability'] == 'undetermined'


def test_center_and_zero_eigenvalues_have_different_behavior(linear):
    times = np.linspace(0, 10, 101)
    center = linear['linear_reference']([[0., 1.], [-1., 0.]], [0., 1.], times)
    shear = linear['linear_reference']([[0., 1.], [0., 0.]], [0., 1.], times)
    neutral = linear['linear_reference'](np.diag([0., -1.]), [1., 1.], times)
    np.testing.assert_allclose(np.linalg.norm(center, axis=0), 1, atol=1e-14)
    np.testing.assert_allclose(shear, [times, np.ones_like(times)])
    np.testing.assert_allclose(neutral, [np.ones_like(times), np.exp(-times)], atol=1e-14)


def test_saddle_can_have_a_convergent_trajectory(answers41):
    stable = answers41['simulate_linear_system'](np.diag([1., -1.]), [0., 1.], 10)
    perturbed = answers41['simulate_linear_system'](np.diag([1., -1.]), [1e-3, 1.], 10)
    assert stable.x1.iloc[-1] == 0
    assert stable.x2.iloc[-1] < 1e-4
    assert perturbed.x1.iloc[-1] > 20


def test_focus_analytic_expm_and_ivp_agree_at_nonzero_initial_time(linear):
    M = np.array([[-.2, 1.], [-1., -.2]])
    times = np.linspace(3, 20, 201)
    s = times-times[0]
    expected = np.exp(-.2*s)*np.array([np.cos(s)+.2*np.sin(s), -np.sin(s)+.2*np.cos(s)])
    np.testing.assert_allclose(linear['linear_reference'](M, [1., .2], times), expected, atol=1e-14)
    np.testing.assert_allclose(linear['solve_linear'](M, [1., .2], times).y, expected,
                               atol=2e-8, rtol=1e-7)


def test_tighter_tolerances_reduce_reference_error(answers41):
    frame = answers41['accuracy_table']([[-.2, 1.], [-1., -.2]], [1., .2],
                                        np.linspace(0, 30, 601), [1e-3, 1e-6, 1e-9])
    assert frame.iloc[-1].max_abs_error < frame.iloc[0].max_abs_error / 1000
    assert frame.iloc[-1].nfev > frame.iloc[0].nfev


def test_repeated_stable_eigenvalue_allows_transient_amplification(answers41, linear):
    M = np.array([[-1., 6.], [0., -1.]])
    exact = expm(M) @ np.array([0., 1.])
    np.testing.assert_allclose(exact, np.exp(-1)*np.array([6., 1.]))
    assert np.linalg.norm(exact) > 2
    assert np.linalg.eigvalsh((M+M.T)/2).max() > 0
    gain = answers41['transient_gain'](M, [0., 1.], np.linspace(0, 10, 1001))
    assert gain['sampled_peak_gain'] > 2
    assert np.linalg.norm(linear['linear_reference'](M, [0., 1.], [0, 20])[:, -1]) < 1e-6


def test_transient_gain_is_invariant_to_uniform_initial_scaling(answers41):
    M = [[-1., 6.], [0., -1.]]
    times = np.linspace(0, 10, 501)
    a = answers41['transient_gain'](M, [0., 1.], times)
    b = answers41['transient_gain'](M, [0., 3.], times)
    np.testing.assert_allclose(a['sampled_peak_gain'], b['sampled_peak_gain'], rtol=1e-7)


@pytest.mark.parametrize('matrix, x0, times', [
    ([[1, 2]], [1], [0, 1]), ([[np.nan]], [1], [0, 1]),
    ([[1j]], [1], [0, 1]), (np.eye(2), [1], [0, 1]),
    (np.eye(2), [1, np.inf], [0, 1]), (np.eye(2), [1, 0], [1, 0]),
    (np.eye(2), [1, 0], [0, 0]), (np.eye(2), [1, 0], [0]),
    (np.eye(2), [1, 0], [0, np.nan]),
])
def test_invalid_linear_inputs_are_rejected(linear, matrix, x0, times):
    with pytest.raises(ValueError):
        linear['solve_linear'](matrix, x0, times)


@pytest.mark.parametrize('kwargs', [dict(rtol=0), dict(atol=-1), dict(rtol=np.inf)])
def test_invalid_tolerances_are_rejected(linear, kwargs):
    with pytest.raises(ValueError):
        linear['solve_linear'](-np.eye(2), [1, 0], [0, 1], **kwargs)


def test_graph_orientation_roundtrip_and_isolated_vertex(network):
    A = np.array([[0., .8, 0., 0.], [0., 0., 1., 0.], [.5, 0., 0., 0.], [0., 0., 0., 0.]])
    G = network['graph_from_A'](A)
    assert set(G.nodes()) == {0, 1, 2, 3}
    assert set(G.edges()) == {(1, 0), (0, 2), (2, 1)}
    np.testing.assert_allclose(nx.to_numpy_array(G, nodelist=range(4)).T, A)
    assert G[1][0]['weight'] == .8
    assert list(network['edge_table'](np.zeros((1, 1))).columns) == ['from', 'to', 'weight']


def test_transposing_reverses_edges_without_changing_eigenvalues(network):
    A = np.array([[0., .8, 0.], [0., 0., 1.], [.5, 0., 0.]])
    assert set(network['graph_from_A'](A).edges()) != set(network['graph_from_A'](A.T).edges())
    np.testing.assert_allclose(np.sort_complex(np.linalg.eigvals(A)),
                               np.sort_complex(np.linalg.eigvals(A.T)))


@pytest.mark.parametrize('n, weight', [(1, 1), (3, 0), (3, 1.5), (6, 2)])
def test_chain_is_nilpotent_and_has_no_eigenvalue_threshold(network, n, weight):
    A = network['chain_matrix'](n, weight)
    np.testing.assert_allclose(np.linalg.matrix_power(A, n), 0)
    frame = network['stability_sweep'](A, .8, [0, .6, 3, 100])
    np.testing.assert_allclose(frame.max_real, -.8)


@pytest.mark.parametrize('n, weight', [(0, 1), (-1, 1), (3.5, 1), (True, 1), (3, -1), (3, np.nan)])
def test_invalid_chain_inputs(network, n, weight):
    with pytest.raises(ValueError):
        network['chain_matrix'](n, weight)


@pytest.mark.parametrize('alpha, beta', [(.8, 0), (.8, 3), (.1, 1.2), (2., .6)])
def test_chain_exact_response_matches_expm_and_ivp(network, alpha, beta):
    A = network['chain_matrix'](3, 1.5)
    M = network['network_matrix'](A, alpha, beta)
    times = np.linspace(2, 8, 121)
    exact = network['chain_exact'](alpha, beta, 1.5, times)
    np.testing.assert_allclose(network['linear_reference'](M, [1., 0., 0.], times), exact, atol=1e-11)
    np.testing.assert_allclose(network['solve_linear'](M, [1., 0., 0.], times).y,
                               exact, rtol=1e-7, atol=2e-7)


def test_cycle_threshold_and_neutral_equilibrium(network):
    A = np.array([[0., .8, 0.], [0., 0., 1.], [.5, 0., 0.]])
    r = np.cbrt(.4)
    beta_c = .8/r
    np.testing.assert_allclose(np.linalg.matrix_power(A, 3), .4*np.eye(3))
    for beta in [0, .6, beta_c, 2]:
        M = network['network_matrix'](A, .8, beta)
        np.testing.assert_allclose(network['spectral_abscissa'](M), -.8+beta*r, atol=1e-14)
    M = network['network_matrix'](A, .8, beta_c)
    neutral = np.array([1., r/.8, r*r/.8])
    np.testing.assert_allclose(M @ neutral, 0, atol=1e-14)
    np.testing.assert_allclose(expm(M*10) @ neutral, neutral, atol=1e-13)


def test_signed_matrix_spectral_radius_is_not_spectral_abscissa(network):
    A = np.array([[0., -1.], [1., 0.]])
    assert max(abs(np.linalg.eigvals(A))) == 1
    assert network['spectral_abscissa'](A) == 0
    np.testing.assert_allclose(network['stability_sweep'](A, .8, [0, 1, 10]).max_real, -.8)


def test_initial_derivatives_and_short_time_path_orders(network):
    A = np.array([[0., .8, 0.], [0., 0., 1.], [.5, 0., 0.]])
    M = network['network_matrix'](A, .8, .6)
    x0 = np.array([1., 0., 0.])
    np.testing.assert_allclose(M @ x0, [-.8, 0., .3])
    h = 1e-5
    end = expm(M*h) @ x0
    assert end[1] > 0  # No positive waiting time before the two-edge response.
    np.testing.assert_allclose([end[2]/h, end[1]/h**2], [.3, .09], rtol=1e-4)


@pytest.mark.parametrize('alpha, beta', [(0, 1), (-1, 1), (np.nan, 1), (1, -1), (1, np.inf)])
def test_invalid_network_parameters(network, alpha, beta):
    with pytest.raises(ValueError):
        network['network_matrix'](np.zeros((3, 3)), alpha, beta)


def test_zero_initial_norm_cannot_define_gain(network, answers41):
    with pytest.raises(ValueError):
        answers41['transient_gain'](-np.eye(2), [0, 0], [0, 1])
    with pytest.raises(ValueError):
        network['network_metrics'](np.zeros((3, 3)), .8, .6, [0, 0, 0], [0, 1])


def test_same_total_weight_does_not_imply_same_stability(network):
    cycle = np.array([[0., 1., 0.], [0., 0., 1.], [1., 0., 0.]])
    chain = network['chain_matrix'](3, 1.5)
    assert cycle.sum() == chain.sum() == 3
    times = np.linspace(0, 20, 501)
    c = network['network_metrics'](cycle, .8, 1., [1., 0., 0.], times)
    h = network['network_metrics'](chain, .8, 1., [1., 0., 0.], times)
    assert c['max_real'] > 0 and h['max_real'] < 0


def test_beta_A_scaling_is_structurally_unidentifiable(network):
    A = np.array([[0., .8, 0.], [0., 0., 1.], [.5, 0., 0.]])
    np.testing.assert_allclose(network['network_matrix'](A, .8, .6),
                               network['network_matrix'](3*A, .8, .6/3))


def test_single_direction_trajectory_cannot_identify_all_coefficients():
    M = np.diag([-1., -2.])
    changed = np.array([[-1., 5.], [0., 3.]])
    initial = np.array([1., 0.])
    for t in [0, 1, 3]:
        np.testing.assert_allclose(expm(M*t) @ initial, expm(changed*t) @ initial, atol=1e-14)


def test_sampled_transition_is_exponential_not_euler_and_need_not_identify_M():
    M = np.array([[0., -2*np.pi], [2*np.pi, 0.]])
    np.testing.assert_allclose(expm(M), np.eye(2), atol=1e-14)
    np.testing.assert_allclose(expm(np.zeros((2, 2))), np.eye(2))
    assert not np.allclose(expm(M), np.eye(2)+M)
