"""Check the stated CA rules and stochastic estimands against exact small cases."""

import ast
from copy import deepcopy
from itertools import product
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


def load_definitions(name, cell_ids):
    cells = {c.id: c for c in nbformat.read(ROOT/'notebooks'/name, 4).cells}
    namespace = {}
    for cell_id in cell_ids:
        nodes = [node for node in ast.parse(cells[cell_id].source).body
                 if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), name, 'exec'), namespace)
    return namespace


@pytest.fixture(scope='module')
def ca():
    return load_definitions('31_train_boarding_ca.ipynb', ['cell-0059', 'cell-0063'])


@pytest.fixture(scope='module')
def stochastic():
    return load_definitions('32_stochastic_simulation_repeats.ipynb', ['imports', 'model'])


def test_distance_field_respects_wall_detour_and_bellman_equation(ca):
    grid = ca['make_grid'](H=5, W=5, door_col=2, door_half=0)
    distance = ca['distance_field'](grid, 4)
    assert distance[0, 1] == 5
    assert np.isinf(distance[0, 2])
    assert distance[2, 1] == 3
    for pos in zip(*np.nonzero(grid)):
        if pos[1] != 4:
            nearby = [p for p in ca['neighbors'](pos, grid.shape) if grid[p]]
            assert distance[pos] == 1+min(distance[p] for p in nearby)


def test_simultaneous_update_cannot_follow_into_a_newly_vacated_cell(ca):
    grid = ca['make_grid'](H=5, W=7, door_col=3, door_half=0)
    agents = [dict(id=i, type='alight', pos=(2, c), done=False) for i, c in enumerate([1, 2])]
    fields = {'alight': ca['distance_field'](grid, 6)}
    proposals = ca['propose_moves'](agents, grid, fields, np.random.default_rng(0))
    assert proposals == {1: (2, 3)}


def test_conflict_has_one_winner_and_no_order_privilege(ca):
    counts = [0, 0]
    for seed in range(1000):
        winners, conflicts = ca['resolve_proposals']({0: (2, 2), 1: (2, 2)}, np.random.default_rng(seed))
        assert len(winners) == 1 and conflicts == 1
        counts[next(iter(winners))] += 1
    assert all(430 < count < 570 for count in counts)


@pytest.mark.parametrize('count', [0, 1, 8, 30])
def test_one_way_completion_bound_and_person_time_conservation(ca, count):
    result = ca['simulate'](n_alight=count, n_board=0, max_steps=1000, seed=11)
    assert result['status'] == 'completed'
    phi = sum(result['fields'][a['type']][a['pos']] for a in result['initial_agents'])
    assert result['completion_time'] <= phi
    assert sum(a['moves'] for a in result['agents']) == phi
    assert result['occupancy_counts'].sum() == sum(a['finished_at'] for a in result['agents'])
    assert all(a['moves']+a['wait_steps'] == a['finished_at'] for a in result['agents'])
    assert np.all(result['occupancy_counts'][~result['passable']] == 0)
    assert np.all((result['occupancy_fraction'] >= 0) & (result['occupancy_fraction'] <= 1))


@pytest.mark.parametrize('cap, status, completion', [(2, 'cutoff', np.nan), (3, 'completed', 3), (8, 'completed', 3)])
def test_exact_horizon_completion_is_not_censoring(ca, cap, status, completion):
    initial = [dict(id=0, type='alight', pos=(2, 1))]
    result = ca['simulate'](H=5, W=5, door_col=2, door_half=0, n_alight=1,
                            initial_agents=initial, max_steps=cap)
    assert result['status'] == status
    if status == 'completed':
        assert result['completion_time'] == completion
    else:
        assert np.isnan(result['completion_time'])
    assert result['capped_time'] == min(cap, 3)
    assert result['occupancy_counts'].sum() == min(cap, 3)


def test_deadlock_is_absorbing_not_early_completion(ca):
    initial = [dict(id=0, type='alight', pos=(2, 1)), dict(id=1, type='board', pos=(2, 3))]
    result = ca['simulate'](H=5, W=5, door_col=2, door_half=0, n_alight=1, n_board=1,
                            initial_agents=initial, max_steps=20)
    assert result['status'] == 'deadlock'
    assert result['remaining'] == 2 and result['steps_evaluated'] == 1
    assert result['capped_time'] == 20 and np.isnan(result['completion_time'])
    assert result['occupancy_counts'].sum() == 40
    for seed in range(10):
        assert ca['propose_moves'](result['agents'], result['passable'], result['fields'], np.random.default_rng(seed)) == {}


def test_same_initial_configuration_is_copied_not_mutated(ca):
    obstacles = [(4, 11), (6, 11)]
    initial = ca['place_agents'](ca['make_grid'](), 10, 8, 0, seed=10, excluded=obstacles)
    saved = deepcopy(initial)
    a = ca['simulate'](initial_agents=initial)
    b = ca['simulate'](initial_agents=initial, obstacles=obstacles)
    assert initial == saved == a['initial_agents'] == b['initial_agents']
    assert not any(agent['pos'] in obstacles for agent in initial)
    assert not b['passable'][4, 11] and not b['passable'][6, 11]


@pytest.mark.parametrize('seed', [7, np.random.SeedSequence(7).spawn(1)[0]])
def test_same_seed_reproduces_history_and_density(ca, seed):
    a = ca['simulate'](n_board=1, seed=seed)
    b = ca['simulate'](n_board=1, seed=seed)
    assert a['agents'] == b['agents'] and a['status'] == b['status']
    pd.testing.assert_frame_equal(a['history'], b['history'])
    np.testing.assert_array_equal(a['occupancy_counts'], b['occupancy_counts'])


@pytest.mark.parametrize('kwargs', [dict(n_alight=-1), dict(n_alight=10000), dict(n_board=1.5),
                                   dict(door_half=6), dict(max_steps=0), dict(obstacles=[(4, 100)]),
                                   dict(obstacles=[(0, 10)])])
def test_ca_rejects_invalid_geometry_or_counts(ca, kwargs):
    with pytest.raises(ValueError):
        ca['simulate'](**kwargs)


def test_initial_overlap_and_unreachable_goal_are_rejected(ca):
    overlap = [dict(id=0, type='alight', pos=(2, 1)), dict(id=1, type='alight', pos=(2, 1))]
    with pytest.raises(ValueError, match='overlapping'):
        ca['simulate'](n_alight=2, initial_agents=overlap)
    with pytest.raises(ValueError, match='cannot reach'):
        ca['simulate'](H=5, W=5, door_col=2, door_half=0, obstacles=[(2, 2)],
                       n_alight=1, initial_agents=[dict(id=0, type='alight', pos=(2, 1))])


def test_bottleneck_uses_one_trial_per_step_and_counts_success_step(stochastic):
    u = np.array([0.1, 0.9, 0.2, 0.8, 0.1, 0.1])
    result = stochastic['simulate_baseline'](n_alight=2, n_board=1, pass_probability=0.5,
                                             max_steps=6, uniforms=u)
    assert result['completion_time'] == 5
    np.testing.assert_array_equal(result['history'], [[0, 2, 1], [1, 1, 1], [2, 1, 1],
                                                      [3, 0, 1], [4, 0, 1], [5, 0, 0]])


@pytest.mark.parametrize('na, nb, p, cap, status, time', [
    (0, 0, 0, 2, 'completed', 0), (2, 3, 1, 5, 'completed', 5),
    (2, 3, 1, 4, 'cutoff', np.nan), (2, 0, 0, 4, 'cutoff', np.nan),
])
def test_bottleneck_endpoint_cases(stochastic, na, nb, p, cap, status, time):
    result = stochastic['simulate_baseline'](n_alight=na, n_board=nb, pass_probability=p, max_steps=cap)
    assert result['status'] == status
    if status == 'completed':
        assert result['completion_time'] == time
    else:
        assert np.isnan(result['completion_time']) and result['capped_time'] == cap


def test_analytic_moments_match_negative_binomial_convention(stochastic):
    for m, p in [(1, 0.3), (44, 0.72), (4, 1.0)]:
        mean, variance = stochastic['analytic_moments'](m, p)
        if p == 1:
            # SciPyの旧版は退化分布の歪度まで評価して警告するため直接検証する．
            assert mean == m and variance == 0
        else:
            assert mean == pytest.approx(stats.nbinom.mean(m, p)+m)
            assert variance == pytest.approx(stats.nbinom.var(m, p))


def test_exact_enumeration_of_censored_distribution(stochastic):
    m, p, cap = 2, 0.3, 4
    probability = mean_capped = 0
    for bits in product([0, 1], repeat=cap):
        weight = p**sum(bits)*(1-p)**(cap-sum(bits))
        uniforms = np.array([0.1 if bit else 0.9 for bit in bits])
        result = stochastic['simulate_baseline'](n_alight=m, n_board=0, pass_probability=p,
                                                 max_steps=cap, uniforms=uniforms)
        probability += weight*result['completed']
        mean_capped += weight*result['capped_time']
    assert probability == pytest.approx(stats.binom.sf(m-1, cap, p))
    assert mean_capped == pytest.approx(stats.nbinom.sf(np.arange(cap)-m, m, p).sum())


def test_independent_repeats_reproduce_and_match_exact_mean(stochastic):
    raw = stochastic['repeat_trials'](n=3000, n_alight=5, n_board=0, pass_probability=0.4, max_steps=200)
    assert raw['completed'].all()
    pd.testing.assert_frame_equal(raw.iloc[:10], stochastic['repeat_trials'](
        n=10, n_alight=5, n_board=0, pass_probability=0.4, max_steps=200))
    mean, variance = stochastic['analytic_moments'](5, 0.4)
    assert abs(raw['completion_time'].mean()-mean) < 5*np.sqrt(variance/len(raw))
    assert raw['completion_time'].var(ddof=1) == pytest.approx(variance, rel=0.1)


def test_standard_error_is_sample_sd_divided_by_root_n(stochastic):
    sample = np.array([40, 42, 43, 45, 80])
    result = stochastic['mean_summary'](sample)
    assert result['mean'] == 50 and result['median'] == 43
    assert result['se'] == pytest.approx(sample.std(ddof=1)/np.sqrt(5))
    assert result['ci_high']-result['mean'] == pytest.approx(stats.t.ppf(0.975, 4)*result['se'])
    with pytest.raises(ValueError):
        stochastic['mean_summary']([40, np.nan])


@pytest.mark.parametrize('successes', [0, 1, 20, 40])
def test_wilson_endpoints_remain_valid_with_zero_or_all_successes(stochastic, successes):
    low, high = stochastic['wilson_interval'](successes, 40)
    assert 0 <= low <= successes/40 <= high <= 1
    assert high > low
    if successes == 0:
        assert low == 0
    if successes == 40:
        assert high == 1


def test_common_time_uniforms_give_monotone_bottleneck_coupling(stochastic):
    rows = []
    for seed in range(100):
        uniforms = np.random.default_rng(seed).random(100)
        base = stochastic['simulate_baseline'](pass_probability=0.65, uniforms=uniforms, max_steps=100)
        alt = stochastic['simulate_baseline'](pass_probability=0.8, uniforms=uniforms, max_steps=100)
        assert alt['capped_time'] <= base['capped_time']
        rows.append([base['capped_time'], alt['capped_time']])
    values = np.array(rows)
    differences = values[:, 1]-values[:, 0]
    covariance = np.cov(values.T, ddof=1)
    assert differences.var(ddof=1) == pytest.approx(covariance[0, 0]+covariance[1, 1]-2*covariance[0, 1])


@pytest.mark.parametrize('kwargs', [dict(pass_probability=-0.1), dict(pass_probability=1.1),
                                   dict(pass_probability=np.nan), dict(n_alight=-1), dict(max_steps=0),
                                   dict(uniforms=[0.1])])
def test_bottleneck_rejects_invalid_inputs(stochastic, kwargs):
    with pytest.raises(ValueError):
        stochastic['simulate_baseline'](**kwargs)


@pytest.mark.parametrize('main, cell_id, solution', [
    ('31_train_boarding_ca.ipynb', 'cell-0063', '31_train_boarding_ca_solutions.ipynb'),
    ('32_stochastic_simulation_repeats.ipynb', 'model', '32_stochastic_simulation_repeats_solutions.ipynb'),
])
def test_solution_functions_match_the_taught_functions(main, cell_id, solution):
    main_cells = {c.id: c for c in nbformat.read(ROOT/'notebooks'/main, 4).cells}
    solution_cells = {c.id: c for c in nbformat.read(ROOT/'notebooks'/'solutions'/solution, 4).cells}
    def functions(source):
        return {node.name: ast.dump(node) for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}
    assert functions(main_cells[cell_id].source) == functions(solution_cells['setup'].source)
