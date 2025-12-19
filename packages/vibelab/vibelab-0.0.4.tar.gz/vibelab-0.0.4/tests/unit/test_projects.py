from vibelab.db.connection import get_db_path, get_project_home, get_results_dir


def test_project_scoped_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("VIBELAB_HOME", str(tmp_path))

    monkeypatch.setenv("VIBELAB_PROJECT", "alpha")
    assert get_project_home() == tmp_path / "projects" / "alpha"
    assert get_db_path() == tmp_path / "projects" / "alpha" / "data.db"
    assert get_results_dir() == tmp_path / "projects" / "alpha" / "results"

    monkeypatch.setenv("VIBELAB_PROJECT", "beta")
    assert get_project_home() == tmp_path / "projects" / "beta"
    assert get_db_path() == tmp_path / "projects" / "beta" / "data.db"
    assert get_results_dir() == tmp_path / "projects" / "beta" / "results"


def test_project_name_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("VIBELAB_HOME", str(tmp_path))
    monkeypatch.setenv("VIBELAB_PROJECT", "bad/name")

    try:
        get_project_home()
        assert False, "Expected ValueError for invalid project name"
    except ValueError:
        pass


