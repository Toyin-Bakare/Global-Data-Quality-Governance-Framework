from transformer.sql_renderer import render_sql

def test_render_sql_variables():
    sql = "SELECT '{{ env }}' AS env, {{ macros.ident('col') }} AS x"
    out = render_sql(sql, variables={"env": "local"})
    assert "local" in out
    assert "`col`" in out
