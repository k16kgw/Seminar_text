"""Test added chapter snippets and analytical claims without changing research data."""

import ast
from pathlib import Path
import re

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import solve_banded
from scipy.special import ive

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = [ROOT / 'chapters' / name for name in [
    '11_stegosaurus_heat_basic.md', '12_stegosaurus_heat_shape.md',
    '13_stegosaurus_research_roadmap.md']]


def python_blocks(path):
    return re.findall(r'^```python\n(.*?)^```\s*$', path.read_text(), flags=re.M | re.S)


@pytest.fixture(scope='module')
def snippets():
    namespace = {}
    for path in CHAPTERS:
        for source in python_blocks(path):
            nodes = [n for n in ast.parse(source).body
                     if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
            exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


@pytest.mark.parametrize('path', CHAPTERS, ids=lambda p: p.stem)
def test_all_chapter_python_fragments_parse(path):
    for source in python_blocks(path):
        ast.parse(source)


@pytest.mark.parametrize('name', [
    '11_variable_width_balance', '12_base_condition_choices',
    '12_cut_cell_geometry', '13_shape_comparison_design'])
def test_teaching_figures_have_editable_sources(name):
    folder = ROOT / 'assets' / 'figures' / 'learning'
    assert (folder / f'{name}.png').read_bytes().startswith(b'\x89PNG')
    assert '<svg' in (folder / f'{name}.svg').read_text()


@pytest.mark.parametrize('n, contact', [(5, .1), (8, .13), (17, .5), (1, .23)])
def test_partial_heating_preserves_contact_length_even_off_grid(snippets, n, contact):
    edges = np.linspace(-.25, .25, n+1)
    lengths = snippets['heated_lengths'](edges, contact)
    np.testing.assert_allclose(lengths.sum(), contact, atol=1e-15)
    assert np.all(lengths >= 0)
    assert np.all(lengths <= np.diff(edges)+1e-15)
    np.testing.assert_allclose(lengths, lengths[::-1], atol=1e-15)


@pytest.mark.parametrize('edges, width', [([0], .1), ([0, 0], .1), ([1, 0], .1),
                                        ([-.2, .2], .5), ([-.2, .2], 0),
                                        ([-.2, np.nan], .1), ([-.2, .2], np.inf)])
def test_invalid_contact_geometry_is_rejected(snippets, edges, width):
    with pytest.raises(ValueError):
        snippets['heated_lengths'](edges, width)


def test_partial_base_conductance_snippet_separates_heating_and_loss(snippets):
    source = next(s for s in python_blocks(CHAPTERS[1]) if s.startswith('x_edges ='))
    ns = dict(snippets, width=.5, nx=8, dx_cell=.5/8, dy_cell=.05, kt=.4,
              contact_width=.13, h_unheated_base=0., thickness_value=.02, k_value=20.)
    exec(source, ns)
    np.testing.assert_allclose(ns['g_b_vec'].sum(), .4*.13/(.05/2))
    np.testing.assert_allclose(ns['g_0_vec'], 0)
    ns['h_unheated_base'] = 10.
    exec(source, ns)
    expected = 10*.02*(.5-.13)/(1+10*.05/(2*20))
    np.testing.assert_allclose(ns['g_0_vec'].sum(), expected)
    assert np.any((ns['length_h'] > 0) & (ns['length_0'] > 0))


def test_single_cut_cell_fraction_and_empty_and_full_cases(snippets):
    area = snippets['cell_area_fraction']
    w = lambda y: 2*(1.4-y)
    np.testing.assert_allclose(area(0, 1, 0, 1, w, nsub=1000), .82, atol=1e-14)
    np.testing.assert_allclose(area(0, .2, 0, .2, w), 1, atol=1e-14)
    np.testing.assert_allclose(area(2, 3, 0, 1, w), 0, atol=1e-14)


def test_active_cell_index_uses_no_unknowns_outside_domain(snippets):
    source = next(s for s in python_blocks(CHAPTERS[1]) if 'active = phi > phi_min' in s)
    ns = dict(snippets, phi=np.array([[0, 1], [.25, 0.]]), phi_min=1e-10)
    exec(source, ns)
    np.testing.assert_array_equal(ns['index'], [[-1, 0], [1, -1]])
    assert ns['A'].shape == (2, 2)


@pytest.mark.parametrize('s', [-.8, -.5, 0., .5, 1.])
def test_trapezoid_area_and_endpoint_widths(snippets, s):
    a = snippets['trapezoid_width']
    area = quad(lambda x: float(a(x, s)), 0, 1)[0]
    np.testing.assert_allclose(area, .5, atol=1e-14)
    np.testing.assert_allclose(a([0, 1], s), [.5*(1+s), .5*(1-s)], atol=1e-14)


@pytest.mark.parametrize('xi, s, width', [([0, 1], -1., .5), ([0, 1], 1.1, .5),
                                       ([-.1], 0., .5), ([0], 0., -1), ([np.nan], 0, .5)])
def test_invalid_width_function_inputs(snippets, xi, s, width):
    with pytest.raises(ValueError):
        snippets['trapezoid_width'](xi, s, width)


@pytest.mark.parametrize('lam', [.1, .5, 2., 8., 30.])
def test_triangle_bessel_flux_agrees_with_face_integral(snippets, lam):
    Q = snippets['triangle_reference_heat'](lam)
    # Equal width ratio 0.5: a(xi) = 1-xi. Scaled Bessel ratio avoids overflow.
    U = lambda xi: np.exp(-lam*xi)*ive(0, lam*(1-xi))/ive(0, lam)
    integral = lam**2*quad(lambda xi: (1-xi)*U(xi), 0, 1, epsabs=1e-12)[0]
    np.testing.assert_allclose(Q, integral, rtol=2e-11)


def test_large_lambda_reference_remains_finite(snippets):
    assert np.isfinite(snippets['triangle_reference_heat'](1000.))


@pytest.mark.parametrize('lam, width', [(0, .5), (-1, .5), (1, 0), (np.nan, .5), (1, np.inf)])
def test_invalid_triangle_reference_parameters(snippets, lam, width):
    with pytest.raises(ValueError):
        snippets['triangle_reference_heat'](lam, width)


def test_small_lambda_absolute_and_relative_differences_have_distinct_orders(snippets):
    absolute, relative = [], []
    for lam in [.08, .04, .02]:
        rect = .5*lam*np.tanh(lam)
        tri = snippets['triangle_reference_heat'](lam)
        absolute.append(tri-rect)
        relative.append(tri/rect-1)
    np.testing.assert_allclose(np.asarray(absolute[:-1])/absolute[1:], 16, rtol=.01)
    np.testing.assert_allclose(np.asarray(relative[:-1])/relative[1:], 4, rtol=.01)
    # J_rect - J_triangle = width_ratio*(1/3 - 1/8).
    np.testing.assert_allclose(absolute[-1]/.02**4, .5*(1/3-1/8), rtol=.001)


def width_fin_discretization(a, lam, n):
    """Independent implementation of the cell-balance formula printed in chapter 11."""
    d = 1./n
    centers = (np.arange(n)+.5)*d
    g = a(np.arange(1, n)*d)/d
    loss = lam**2*a(centers)*d
    diag = loss.copy()
    diag[:-1] += g
    diag[1:] += g
    gb = float(a(np.array([0.]))[0])/(d/2)
    diag[0] += gb
    bands = np.zeros((3, n))
    bands[0, 1:] = -g
    bands[1] = diag
    bands[2, :-1] = -g
    rhs = np.zeros(n)
    rhs[0] = gb
    U = solve_banded((1, 1), bands, rhs)
    return centers, U, gb*(1-U[0]), np.dot(loss, U)


@pytest.mark.parametrize('s', [0., 1.])
def test_taught_variable_width_balance_recovers_known_solutions(snippets, s):
    lam = 2.
    a = lambda xi: snippets['trapezoid_width'](xi, s)
    exact_Q = .5*lam*np.tanh(lam) if s == 0 else snippets['triangle_reference_heat'](lam)
    errors = []
    for n in [40, 80, 160]:
        x, U, qbase, qface = width_fin_discretization(a, lam, n)
        np.testing.assert_allclose(qbase, qface, atol=1e-10)
        assert 0 < U.min() <= U.max() < 1
        errors.append(abs(qface-exact_Q))
    assert errors[-1] < errors[0]/10


def test_physical_dimensionless_mapping_and_validity_flag(snippets):
    p = snippets['dimensional_parameters'](.5, .02, .5, 5.)
    np.testing.assert_allclose(p['Bi_L'], p['lam']**2*p['tau']/2)
    np.testing.assert_allclose(p['Bi_t'], p['lam']**2*p['tau']**2/4)
    np.testing.assert_allclose(p['thermal_length'], np.sqrt(.5*.02/(2*5)))
    np.testing.assert_allclose(p['Bi_t'], .1)
    assert 16**2*.1**2/4 > .5


def test_difference_summary_does_not_confuse_small_difference_change_with_exactness(snippets):
    # Both heat values have a common grid-dependent bias.
    result = snippets['grid_difference_summary']([2.4, 2.2, 2.1], [1.4, 1.2, 1.1])
    np.testing.assert_allclose(result['D_fine'], 1.)
    assert result['change_shape'] > .09 and result['change_reference'] > .09
    assert result['change_difference'] < 1e-14


def test_example_case_table_contains_eighteen_unique_conditions(snippets):
    source = next(s for s in python_blocks(CHAPTERS[2]) if 'cases = pd.DataFrame' in s)
    ns = dict(snippets)
    exec(source, ns)
    assert len(ns['cases']) == 18


def test_oblique_cell_geometry_numbers_in_caption():
    cut = 1.4
    outside_triangle_side = 2-cut
    np.testing.assert_allclose(1-outside_triangle_side**2/2, .82)
    np.testing.assert_allclose(cut-1, .4)
    np.testing.assert_allclose(np.hypot(outside_triangle_side, outside_triangle_side), .6*np.sqrt(2))
