import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_rollbacks():
    """Test that directories are found and added to sys.path"""
    orig_syspath = sorted(sys.path.copy(), key=str)

    # this import is only needed for fupi tests, pip installs will work fine.
    from fupi.fupi import ManualFupi 
    mf = ManualFupi(autorun=True)

    # fupi grabs a snapshot of sys.path before and after modifying it
    assert len(mf.sys_path_history) == 2

    mf.run() # snapshots are only taken if there is a change in data
    assert len(mf.sys_path_history) == 2 # no change, so no new snapshot

    assert mf.sys_path_history[0] == orig_syspath

    sys.path = mf.sys_path_history[0] # Reset sys.path to pre-import state
    sys.path = mf.sys_path_history[-1] # Reset sys.path to the last known state
    
    pass
 
 
if __name__ == '__main__':
    test_rollbacks()
    pass