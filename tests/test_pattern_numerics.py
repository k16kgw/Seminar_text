"""Verify the chapter 21 solver and chapter 22 measurements, including edge cases."""

import ast
from pathlib import Path

import nbformat
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def definitions(notebook_name, cell_ids):
    cells = {cell.id: cell for cell in nbformat.read(ROOT / 'notebooks' / notebook_name, 4).cells}
    namespace = {}
    for cell_id in cell_ids:
        tree = ast.parse(cells[cell_id].source)
        nodes = [node for node in tree.body
                 if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), notebook_name, 'exec'), namespace)
    return namespace


@pytest.fixture(scope='module')
def gs():
    return definitions('21_reaction_diffusion_gray_scott.ipynb',
                       ['cell-0031', 'cell-0035', 'cell-0037', 'growth-function'])


@pytest.fixture(scope='module')
def features():
    return definitions('22_snake_pattern_features.ipynb', ['imports', 'patterns', 'features'])


def test_gray_scott_trivial_equilibrium_has_no_turing_instability(gs):
    q = np.linspace(0, 20, 201)
    actual = gs['growth_rates'](np.diag([-0.035, -0.1]), 0.16, 0.08, q)
    expected = np.maximum(-0.035-0.16*q**2, -0.1-0.08*q**2)
    np.testing.assert_allclose(actual, expected)
    assert np.all(actual < 0)


def test_illustrative_turing_band_and_equal_diffusion(gs):
    J = np.array([[1, -2], [2, -3]])
    q = np.linspace(0, 10, 401)
    growth = gs['growth_rates'](J, 0.01, 0.1, q)
    assert growth[0] < 0 and growth.max() > 0 and growth[-1] < 0
    assert np.all(gs['growth_rates'](J, 0.1, 0.1, q) < 0)


def test_initial_fields_are_nonnegative_reproducible_and_grid_consistent(gs):
    u, v = gs['initial_fields'](24, 24, seed=3)
    uf, vf = gs['initial_fields'](48, 24, seed=3)
    assert min(u.min(), v.min()) >= 0
    np.testing.assert_allclose(u, uf[::2, ::2], rtol=0, atol=0)
    np.testing.assert_allclose(v, vf[::2, ::2], rtol=0, atol=0)
    assert not np.array_equal(v, gs['initial_fields'](24, 24, seed=4)[1])
    u0, v0 = gs['initial_fields'](24, 24, amplitude=0)
    np.testing.assert_array_equal(u0, np.ones_like(u0))
    np.testing.assert_array_equal(v0, np.zeros_like(v0))


def test_trivial_equilibrium_is_preserved_exactly(gs):
    result = gs['gray_scott'](N=8, length=8, t_end=17.3, dt=0.7,
                              initial=(np.ones((8, 8)), np.zeros((8, 8))))
    np.testing.assert_array_equal(result['u'], np.ones((8, 8)))
    np.testing.assert_array_equal(result['v'], np.zeros((8, 8)))
    assert result['dt'] <= 0.7
    assert result['dt']*result['steps'] == pytest.approx(17.3)
    assert result['snapshots'][-1][0] == pytest.approx(17.3)


def test_laplacian_is_conservative_and_contains_grid_spacing(gs):
    field = np.random.default_rng(2).random((12, 15))
    lap = gs['laplacian'](field, 0.5)
    assert abs(lap.sum()) < 1e-12
    np.testing.assert_allclose(lap, 4*gs['laplacian'](field, 1))
    np.testing.assert_array_equal(gs['laplacian'](np.ones((5, 7)), 0.5), np.zeros((5, 7)))


def test_step_uses_old_values_and_correct_global_balance(gs):
    rng = np.random.default_rng(4)
    u, v = 0.5+0.2*rng.random((10, 10)), 0.1+0.1*rng.random((10, 10))
    dt, F, k = 0.1, 0.035, 0.065
    un, vn = gs['gray_scott_step'](u, v, 0.16, 0.08, F, k, 1, dt)
    np.testing.assert_allclose(un, u+dt*(0.16*gs['laplacian'](u, 1)-u*v*v+F*(1-u)))
    np.testing.assert_allclose(vn, v+dt*(0.08*gs['laplacian'](v, 1)+u*v*v-(F+k)*v))
    change = (un+vn-u-v).sum()
    expected = dt*(F*(1-u)-(F+k)*v).sum()
    assert change == pytest.approx(expected, abs=1e-13)


def test_time_error_is_first_order(gs):
    errors = []
    for dt in [1.0, 0.5, 0.25]:
        result = gs['gray_scott'](N=8, length=8, t_end=20, dt=dt,
                                  initial=(np.full((8, 8), 0.7), np.zeros((8, 8))))
        errors.append(np.max(abs(result['u']-(1-0.3*np.exp(-0.035*20)))))
    ratios = np.array(errors[:-1])/errors[1:]
    assert np.all((ratios > 1.95) & (ratios < 2.1)), ratios


def test_diffusion_converges_quadratically_at_fixed_domain_and_time(gs):
    errors = []
    for n in [16, 32, 64]:
        dx, length, end = 16/n, 16, 2
        x = np.tile(np.arange(n)*dx, (n, 1))
        u0 = 1+0.1*np.cos(2*np.pi*x/length)
        result = gs['gray_scott'](N=n, length=length, t_end=end, dt=0.2*dx**2,
                                  Du=0.16, Dv=0, F=0, k=0, initial=(u0, np.zeros_like(u0)))
        exact = 1+0.1*np.exp(-0.16*(2*np.pi/length)**2*end)*np.cos(2*np.pi*x/length)
        errors.append(np.max(abs(result['u']-exact)))
        assert result['u'].mean() == pytest.approx(u0.mean(), abs=2e-14)
    ratios = np.array(errors[:-1])/errors[1:]
    assert np.all((ratios > 3.8) & (ratios < 4.2)), ratios


@pytest.mark.parametrize('kwargs', [dict(dt=2), dict(length=0), dict(F=-1), dict(dt=np.nan), dict(N=4.5)])
def test_solver_rejects_invalid_parameters(gs, kwargs):
    settings = dict(N=8, length=8, t_end=2)
    settings.update(kwargs)
    with pytest.raises(ValueError):
        gs['gray_scott'](**settings)


def test_negative_concentrations_are_not_silently_clipped(gs):
    initial = (np.ones((8, 8)), -np.ones((8, 8)))
    with pytest.raises(ValueError, match='nonnegative'):
        gs['gray_scott'](N=8, length=8, t_end=1, initial=initial)
    # Diffusion CFL alone does not protect an explicit fast reaction step.
    with pytest.raises(FloatingPointError, match='negative'):
        gs['gray_scott'](N=8, length=8, t_end=1, Du=0, Dv=0,
                         initial=(np.ones((8, 8)), 10*np.ones((8, 8))))


def test_area_and_components_measure_different_properties(features):
    a, b = np.zeros((64, 64)), np.zeros((64, 64))
    a[24:40, 24:40] = 1
    for y in (12, 44):
        for x in (12, 44):
            b[y:y+8, x:x+8] = 1
    assert features['area_fraction'](a) == features['area_fraction'](b) == 0.0625
    assert features['component_count'](a) == 1
    assert features['component_count'](b) == 4


def test_diagonal_neighborhood_and_periodic_corners(features):
    a = np.eye(2)
    assert features['component_count'](a, connectivity=4) == 2
    assert features['component_count'](a, connectivity=8) == 1
    a = np.zeros((5, 7))
    a[0, 0] = a[-1, -1] = 1
    assert features['component_count'](a, periodic=False) == 2
    assert features['component_count'](a, connectivity=4, periodic=True) == 2
    assert features['component_count'](a, connectivity=8, periodic=True) == 1


def reference_periodic_count(binary, connectivity):
    remaining = set(zip(*np.nonzero(binary)))
    offsets = [(dy, dx) for dy in [-1, 0, 1] for dx in [-1, 0, 1]
               if (dy or dx) and (connectivity == 8 or abs(dy)+abs(dx) == 1)]
    count = 0
    while remaining:
        count += 1
        stack = [remaining.pop()]
        while stack:
            y, x = stack.pop()
            for dy, dx in offsets:
                neighbor = ((y+dy) % binary.shape[0], (x+dx) % binary.shape[1])
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    return count


@pytest.mark.parametrize('connectivity', [4, 8])
def test_periodic_labels_match_independent_graph_traversal(features, connectivity):
    rng = np.random.default_rng(14)
    for density in [0, 0.1, 0.4, 0.8, 1]:
        for _ in range(5):
            binary = rng.random((9, 13)) < density
            assert features['component_count'](binary, connectivity=connectivity, periodic=True) == reference_periodic_count(binary, connectivity)


@pytest.mark.parametrize('wavelength', [16, 32, 192])
def test_known_wavelength_including_first_nonzero_frequency(features, wavelength):
    field = features['make_stripes'](wavelength=wavelength)
    assert features['dominant_wavelength'](field) == pytest.approx(wavelength)


@pytest.mark.parametrize('value', [0, 1, -3])
def test_constant_image_has_no_defined_wavelength(features, value):
    assert np.isnan(features['dominant_wavelength'](np.full((24, 48), value)))


def test_rectangular_image_with_unequal_pixel_spacings(features):
    ny, nx, dy, dx = 60, 96, 2, 0.5
    yy, xx = np.mgrid[:ny, :nx]
    field = np.cos(2*np.pi*(4*xx/nx+3*yy/ny))
    expected = 1/np.hypot(4/(nx*dx), 3/(ny*dy))
    assert features['dominant_wavelength'](field, pixel_size=(dy, dx)) == pytest.approx(expected)


def test_parseval_and_equal_variance_do_not_imply_equal_wavelength(features):
    a, b = (features['make_stripes'](wavelength=w) for w in [16, 32])
    assert a.var() == pytest.approx(b.var())
    assert features['dominant_wavelength'](a) != features['dominant_wavelength'](b)
    assert features['spectrum_data'](a)[2].sum() == pytest.approx(a.var())


def test_periodic_shift_preserves_fft_but_open_components_can_change(features):
    a = np.zeros((32, 32))
    a[10:22, 10:22] = 1
    b = np.roll(a, 16, axis=1)
    np.testing.assert_allclose(features['spectrum_data'](a)[2], features['spectrum_data'](b)[2], atol=1e-14)
    assert features['area_fraction'](a) == features['area_fraction'](b)
    assert features['component_count'](a) == 1 and features['component_count'](b) == 2
    assert features['component_count'](a, periodic=True) == features['component_count'](b, periodic=True) == 1


def test_threshold_demo_uses_grayscale_as_well_as_binary_control(features):
    spots = features['make_spots']()
    stripes = features['make_stripes']()
    assert len({features['area_fraction'](spots, threshold=t) for t in [0.3, 0.5, 0.7]}) == 1
    assert len({features['area_fraction'](stripes, threshold=t) for t in [0.3, 0.5, 0.7]}) == 3


@pytest.mark.parametrize('kwargs', [dict(pixel_size=0), dict(pixel_size=(1, -1)),
                                   dict(pixel_size=(1, 2, 3)), dict(contrast_tol=-1)])
def test_wavelength_rejects_invalid_units(features, kwargs):
    with pytest.raises(ValueError):
        features['dominant_wavelength'](np.eye(10), **kwargs)


def test_component_count_rejects_ambiguous_settings(features):
    with pytest.raises(ValueError, match='connectivity'):
        features['component_count'](np.eye(4), connectivity=6)
    with pytest.raises(ValueError, match='threshold'):
        features['component_count'](np.eye(4), threshold=np.nan)


@pytest.mark.parametrize('main, cell_ids, solution', [
    ('21_reaction_diffusion_gray_scott.ipynb', ['cell-0035', 'cell-0037'],
     '21_reaction_diffusion_gray_scott_solutions.ipynb'),
    ('22_snake_pattern_features.ipynb', ['patterns', 'features'],
     '22_snake_pattern_features_solutions.ipynb'),
])
def test_solution_setup_matches_the_taught_functions(main, cell_ids, solution):
    source_cells = {c.id: c for c in nbformat.read(ROOT/'notebooks'/main, 4).cells}
    solution_cells = {c.id: c for c in nbformat.read(ROOT/'notebooks'/'solutions'/solution, 4).cells}
    functions = lambda source: {n.name: ast.dump(n) for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
    expected = {}
    for cell_id in cell_ids:
        expected.update(functions(source_cells[cell_id].source))
    assert expected == functions(solution_cells['setup'].source)
