import sys, shutil, tempfile, os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_shortest_path_manual():
    """Test the "shortest_path" property of ManualFupi class."""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'src/subdir1a').mkdir()
            (Path(tmpdir) / 'src/subdir1a/subdir2a').mkdir()
            (Path(tmpdir) / 'src/subdir1b').mkdir()
            (Path(tmpdir) / 'src/subdir1b/subdir2b').mkdir()
            (Path(tmpdir) / '.git').mkdir()
            (Path(tmpdir) / '__pycache__').mkdir()
            
            from fupi.fupi import ManualFupi
            mf = ManualFupi(autorun=True)
            paths = mf.get_paths()

            # Should not include hidden or underscore directories
            assert not any('__pycache__' in str(p) for p in sys.path)
            assert not any('.git' in str(p) for p in sys.path)
            
            # if no path list supplied, will use last run's sys.path subset
            spaths_man_calc = sorted(mf.get_paths(), key=lambda p: (len(p.parts), p.as_posix()))
            spath = mf.shortest_path()  
            assert spath == spaths_man_calc[0], "Shortest path without args does not match expected"
            
            # if you want, you can supply a list of paths to evaluate instead
            spaths_man_calc = sorted([Path(p) for p in sys.path], key=lambda p: (len(p.parts), p.as_posix()))
            spath = mf.shortest_path(sys.path)
            assert spath == spaths_man_calc[0], "Shortest path without args does not match expected"

            pass

    finally:
        shutil.rmtree(tmpdir, True)
        os.chdir(original_cwd)
 
 
def test_shortest_path_auto():
    """Test the "shortest_path" property of AutoFupi instance."""
    original_cwd = os.getcwd()
    import fupi.fupi as fupi_mod
    print(fupi_mod.shortest_path)
    pass



if __name__ == '__main__':
    test_shortest_path_auto()
    test_shortest_path_manual()
    pass