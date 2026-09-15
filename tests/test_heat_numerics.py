"""Check the taught solvers against analytical solutions and conservation laws."""

import ast
from pathlib import Path

import nbformat
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_solver(notebook_name, parameter_ids, solver_id):
    cells = {c.id: c for c in nbformat.read(ROOT / 'notebooks' / notebook_name, 4).cells}
    namespace = {}
    for cell_id in parameter_ids:
        exec(cells[cell_id].source, namespace)
    tree = ast.parse(cells[solver_id].source)
    definitions = ast.Module(
        body=[node for node in tree.body if isinstance(node, ast.FunctionDef)],
        type_ignores=[],
    )
    exec(compile(definitions, notebook_name, 'exec'), namespace)
    return namespace


@pytest.fixture(scope='module')
def fin():
    return load_solver('11_stegosaurus_heat_1d_fin.ipynb',
                       ['cell-0002', 'cell-0004'], 'cell-0006')


@pytest.fixture(scope='module')
def plate():
    return load_solver('12_stegosaurus_single_plate_2d.ipynb', ['parameters'], 'solver')


def test_fin_heat_uses_the_requested_convection_coefficient(fin):
    for h_value in [10.0, 25.0, 50.0]:
        m = np.sqrt(h_value * fin['P'] / (fin['k'] * fin['A_c']))
        actual = fin['Q_fin'](fin['L'], m, fin['theta_b'], fin['k'], fin['A_c'])
        expected = np.sqrt(h_value * fin['P'] * fin['k'] * fin['A_c']) * fin['theta_b'] * np.tanh(m * fin['L'])
        np.testing.assert_allclose(actual, expected, rtol=1e-13)


def test_fin_temperature_and_heat_converge_quadratically(fin):
    errors = []
    q_exact = fin['Q_fin'](fin['L'], fin['m'], fin['theta_b'], fin['k'], fin['A_c'])
    for n in [41, 81, 161]:
        x, theta = fin['theta_fd'](fin['L'], fin['m'], fin['theta_b'], n=n)
        dx = x[1] - x[0]
        exact = fin['theta_analytic'](x, fin['L'], fin['m'], fin['theta_b'])
        q_base = -fin['k']*fin['A_c']*(-3*theta[0] + 4*theta[1] - theta[2])/(2*dx)
        q_side = fin['h']*fin['P']*fin['trapezoid'](theta, x)
        errors.append([np.max(abs(theta - exact))/fin['theta_b'],
                       abs(q_base/q_exact-1), abs(q_side/q_exact-1)])
    ratios = np.asarray(errors)[:-1] / np.asarray(errors)[1:]
    assert np.all((ratios > 3.7) & (ratios < 4.2)), ratios


@pytest.mark.parametrize('h_tip', [0.0, 25.0])
def test_plate_matches_1d_solution_with_the_same_boundary_conditions(plate, h_tip):
    k, h, t, L, W = [plate[s] for s in ['k', 'h', 'thickness', 'height', 'width']]
    theta_b = plate['T_base'] - plate['T_air']
    mu = np.sqrt(2*h/(k*t))
    tip_ratio = h_tip/(k*mu)
    denom = np.cosh(mu*L) + tip_ratio*np.sinh(mu*L)
    q_exact = k*t*W*mu*theta_b * (np.sinh(mu*L) + tip_ratio*np.cosh(mu*L)) / denom
    errors = []
    for dx in [0.01, 0.005, 0.0025]:
        result = plate['solve_rectangular_plate'](dx=dx, h_side=0, h_tip=h_tip)
        y = result['y']
        exact = theta_b*(np.cosh(mu*(L-y)) + tip_ratio*np.sinh(mu*(L-y)))/denom
        error_t = np.max(abs(result['temperature'] - plate['T_air'] - exact[:, None]))/theta_b
        errors.append([error_t, abs(result['Q_out']/q_exact-1)])
        assert result['balance_error'] < 1e-10
        tip_exact = plate['T_air'] + theta_b/denom
        np.testing.assert_allclose(result['tip_temperature'], tip_exact, atol=2e-3, rtol=0)
    ratios = np.asarray(errors)[:-1] / np.asarray(errors)[1:]
    assert np.all((ratios > 3.6) & (ratios < 4.3)), ratios
    assert max(errors[-1]) < 2e-4


@pytest.mark.parametrize('dx', [0.011, 0.005])
@pytest.mark.parametrize('partial', [False, True])
def test_plate_geometry_bounds_symmetry_and_conservation(plate, dx, partial):
    selector = (lambda ix, x: abs(x[ix]) < 0.04) if partial else None
    result = plate['solve_rectangular_plate'](dx=dx, base_selector=selector)
    T = result['temperature']
    assert T.min() >= plate['T_air'] - 1e-10
    assert T.max() <= plate['T_base'] + 1e-10
    np.testing.assert_allclose(T, T[:, ::-1], atol=1e-9, rtol=0)
    np.testing.assert_allclose(result['area'], plate['width']*plate['height'], rtol=1e-14)
    np.testing.assert_allclose(result['y'][0], result['dy']/2)
    np.testing.assert_allclose(result['y'][-1] + result['dy']/2, plate['height'])
    assert result['balance_error'] < 1e-10
    assert result['linear_residual'] < 1e-12
    assert result['Q_out'] > 0


def test_plate_insulated_limit(plate):
    result = plate['solve_rectangular_plate'](h_value=0, h_side=0, h_tip=0)
    np.testing.assert_allclose(result['temperature'], plate['T_base'], atol=1e-8, rtol=0)
    assert result['Q_out'] == 0
    assert result['balance_absolute'] < 1e-8
    assert np.isnan(result['balance_error'])


def test_plate_temperature_difference_scaling(plate):
    original = plate['T_base']
    try:
        reference = plate['solve_rectangular_plate']()
        plate['T_base'] = plate['T_air'] + 2*(original - plate['T_air'])
        doubled = plate['solve_rectangular_plate']()
        np.testing.assert_allclose(doubled['Q_out'], 2*reference['Q_out'], rtol=1e-12)
        np.testing.assert_allclose(doubled['temperature'] - plate['T_air'],
                                   2*(reference['temperature'] - plate['T_air']), atol=1e-10, rtol=0)
    finally:
        plate['T_base'] = original
