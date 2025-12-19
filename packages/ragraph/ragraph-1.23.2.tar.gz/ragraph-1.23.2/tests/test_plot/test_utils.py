from ragraph import colors, datasets
from ragraph.plot import mdm, utils
from ragraph.plot.generic import Component


def test_get_subplots():
    cmps = [
        [Component(width=100, height=100), Component(width=300, height=200)],
        [Component(width=50, height=50), Component(height=200)],
    ]
    fig = utils.get_subplots(cmps)
    assert fig
    assert fig.layout.xaxis.domain == (0.0, 0.5)
    assert fig.layout.yaxis2.domain == (0.5, 1.0)


def test_swatchplot():
    from plotly import graph_objs as go

    fig = utils.get_swatchplot(cat=colors.get_categorical(), con=colors.get_continuous())

    assert isinstance(fig.data[0], go.Bar)
    assert isinstance(fig.data[1], go.Bar)


def test_multi_export(tmp_path):
    g = datasets.get("climate_control_mg")
    figures = [mdm([n for n in g.nodes if n.depth == d], g.edges) for d in range(g.max_depth + 1)]
    paths = [tmp_path / f"mdm-{d}.svg" for d in range(g.max_depth + 1)]

    utils.write_images(figures, paths)
