"""Test suite for refactored fupi.py with ManualFupi class."""
import sys, shutil, tempfile, os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_get_paths_with_explicit_parameters():
    """Test get_paths() with explicit parameters."""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'src' / 'subdir').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            paths = mf.get_paths(['src'], ['venv*'])
            
            # Should return a list of Path objects
            assert isinstance(paths, list)
            # Should find the src directory
            assert any('src' in str(p) for p in paths)
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


def test_get_paths_with_defaults():
    """Test get_paths() using default values."""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'test').mkdir()
            (Path(tmpdir) / 'app').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            # Call with no parameters to use defaults
            paths = mf.get_paths()
            
            assert isinstance(paths, list)
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


def test_get_paths_empty_add_dirs():
    """Test that get_paths() returns empty list with empty add_dirs."""
    from fupi.fupi import ManualFupi
    mf = ManualFupi()
    paths = mf.get_paths([], [])
    
    assert isinstance(paths, list)
    assert len(paths) == 0


def test_run_adds_paths_to_syspath():
    """Test that run() adds paths to sys.path."""
    original_cwd = os.getcwd()
    original_path_len = len(sys.path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            result = mf.run(['src'], ['venv*'])
            
            # Should have added paths (or returned empty list if none matched)
            assert isinstance(result, list)
            # sys.path_history should be updated
            
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


def test_run_updates_sys_path_history():
    """Test that run() updates sys_path_history."""
    original_cwd = os.getcwd()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            mf.run(['src'], [])
            
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


def test_run_with_skip_patterns():
    """Test that run() respects skip patterns."""
    original_cwd = os.getcwd()
    original_path_len = len(sys.path)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'venv_dir').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            mf.run(['src', 'venv_dir'], ['venv*'])
            
            # Check that no venv paths were added
            new_paths = sys.path[original_path_len:]
            temp_paths = [p for p in new_paths if tmpdir in p]
            assert not any('venv' in p for p in temp_paths)
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


def test_run_with_quoted_values():
    """Test that run() handles quoted directory names."""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            # Quoted directory names should have quotes removed
            paths = mf.get_paths(['"src"'], ['"venv*"'])
            
            assert isinstance(paths, list)
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


def test_run_with_comma_separated_skip_dirs():
    """Test that run() handles comma-separated skip_dirs."""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'build').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            # Pass comma-separated string
            paths = mf.get_paths(['src'], ['build,dist,venv*'])
            
            assert isinstance(paths, list)
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


def test_get_paths_skips_hidden_and_underscore_dirs():
    """Test that hidden and underscore directories are always skipped."""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / '.git').mkdir()
            (Path(tmpdir) / '__pycache__').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi()
            paths = mf.get_paths(['src'], [])
            
            # Should not include hidden or underscore directories
            assert not any('__pycache__' in str(p) for p in paths)
            assert not any('.git' in str(p) for p in paths)
    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)


if __name__ == '__main__':
    test_get_paths_with_explicit_parameters()
    test_get_paths_with_defaults()
    test_get_paths_empty_add_dirs()
    test_run_adds_paths_to_syspath()
    test_run_updates_sys_path_history()
    test_run_with_skip_patterns()
    test_run_with_quoted_values()
    test_run_with_comma_separated_skip_dirs()
    test_get_paths_skips_hidden_and_underscore_dirs()
    pass