from simulated_city.maplibre_live import _inject_renderer_binding


def test_inject_renderer_binding_minified_export() -> None:
    content = "var vjn={render:EPr};export{oDt as MapLibreRenderer,vjn as default};"
    out = _inject_renderer_binding(content)
    assert "const MapLibreRenderer=oDt;" in out
    assert "export{oDt as MapLibreRenderer" in out


def test_inject_renderer_binding_keeps_existing_binding() -> None:
    content = "const MapLibreRenderer=oDt;export{oDt as MapLibreRenderer};"
    out = _inject_renderer_binding(content)
    assert out == content


def test_inject_renderer_binding_parses_alt_export() -> None:
    content = "export{A$1 as MapLibreRenderer,foo as default};"
    out = _inject_renderer_binding(content)
    assert "const MapLibreRenderer=A$1;" in out
    assert "export{A$1 as MapLibreRenderer" in out
