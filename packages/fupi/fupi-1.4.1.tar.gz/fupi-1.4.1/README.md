# fupi

A brute-force shortcut to fix python import hell. Acronym standing for... um, "Fixing-Up Python Imports."  Sure, let's go with that. 

## Usage

You can use fupi in two ways:

### 1. Auto-Configuration (Quick Start)

Simply import fupi in your project:

```python
import fupi
```

Done - that's all you need! On import, fupi will automatically detect and add common top-level code directories, along with all children directories (minus common excluded patterns) to your sys.path, making imports work seamlessly across your project regardless of your CWD / where you start the code from.  

Practically speaking, it lets you test any code from any location within you project, without hitting "python import hell".

By default, fupi will:
- automatically add to sys.path directories that exactly match
    - `src/`, `app/`, `main/`, `test/`, `tests/`, `mcp/`
- ...and all children directories 
- ...excluding any directory that match the regex patterns:
    - `setup`, `venv.*`, `.*\.egg.*`, `old.*`, `bkup|backup`
    - ...or any directory that starts with a period `.` or underscore `_`

### 2. Auto-Config Options

What if your top-level code directory isn't included in the list above?  i.e., `myapp`?  No problem - Envvars FTW.

You can provide additional directory names/patterns to the lists above by setting the environment variables:

```
FUPI_ADD_DIR_NAMES="myapp, test_myapp, etc"
FUPI_SKIP_DIR_PATTERNS="trial, myvenv, custom.*"
```

- `FUPI_ADD_DIR_NAMES`: Additional directory names to recursively add to sys.path
    - an **exact string match**, so you must specify your exact directory name, i.e., `myapp`, `code`, `my_best_convension_ever`, etc.
- `FUPI_SKIP_DIR_PATTERNS`: Additional directory regex patterns to skip
    - a **regex pattern match**, allowing you to add patterns to exclude, i.e., `doc.*s` will skip both `docs` and `documents`
    - Patterns are regular expressions matched against each directory name (using `re.match`), so patterns are tested against each path element. For example, `setup` matches a directory named `setup`, and `venv.*` matches any directory starting with `venv` (and therefore its children).
    - for help with regex:  https://pythex.org/ 
 
### 3. Manual Configuration

For even MORE control, you can suppress the auto-configuration and configure fupi manually.  This is nice for smaller projects, as it gives you exact control per-file. However, hard-coding directory names for every file is less awesome - if you're using broadly, consider setting environment variables, per the above section.

To escape the autorun behavior, use the `from fupi import ManualFupi` (instead of `import fupi`).  The project will detect the method of import and suppress the autorun, allowing you to config before running.  For example:

```python
from fupi import ManualFupi

mf = ManualFupi(add_dir_names=['src', 'test'],
                skip_dir_patterns = ['setup', 'venv*'], 
                autorun = True)
```

While setting environment variables is additive, manually configuring like above will override defaults, so you'll need to be complete.  If you omit setting a list, it will revert to defaults.

If you perform a manual configuration and still set environment variables `FUPI_ADD_DIR_NAMES` or `FUPI_SKIP_DIR_PATTERNS`, they will be **appended** to the provided (or default) values.

 The constructor also accepts an `autorun` boolean. If `autorun =True` the instance will immediately call `run()` during initialization (convenient for short scripts). By default, in manual mode `autorun=False`.


#### A few examples of calling manual mode:

```python
# if all you're doing is manually setting folder names:
from fupi import ManualFupi
mf = ManualFupi(add_dir_names=['src', 'test'],
                skip_dir_patterns = ['setup', 'venv*'])
mf.run()
```

```python
# anything you don't set reverts to defaults:
from fupi import ManualFupi

mf = ManualFupi(add_dir_names=['src', 'test'])
print(mf.skip_dir_patterns) 
#  ['setup', 'venv.*', '.*\.egg.*', 'old.*', 'bkup|backup']

mf.run()
```


```python
# If you want to ADD one value to a list:
from fupi import ManualFupi

mf = ManualFupi()
mf.skip_dir_patterns.append('ignore')
print(mf.skip_dir_patterns) 
#  ['setup', 'venv.*', '.*\.egg.*', 'old.*', 'bkup|backup', 'ignore']

mf.run()
```


```python
# all in one call:
from fupi import ManualFupi, DEFAULT_ADD_DIR_NAMES, DEFAULT_SKIP_DIR_PATTERNS

mf = ManualFupi(add_dir_names = [*DEFAULT_ADD_DIR_NAMES, 'foo', 'bar'],
                skip_dir_patterns = [*DEFAULT_SKIP_DIR_PATTERNS, 'baz.*'],
                autorun = True )
```

```python
# if you want to preview paths added:
from fupi import ManualFupi

mf = ManualFupi()
print(mf.get_paths()) # returns the list of Paths added to sys.path
mf.run()
```

```python
# or if you're more loquacious:
from fupi import ManualFupi, DEFAULT_ADD_DIR_NAMES, DEFAULT_SKIP_DIR_PATTERNS

mf = ManualFupi()
add =  [*DEFAULT_ADD_DIR_NAMES, 'foo', 'bar']
skip = [*DEFAULT_SKIP_DIR_PATTERNS, 'baz.*']

testpath = '/some/path'
do_import = testpath in mf.get_paths(add, skip)

if do_import: 
    mf.run(add, skip)
```

All that said, in the end this: 
```python
import fupi
```` 
...runs the same code as this:

```python
from fupi import ManualFupi
mf = ManualFupi(autorun=True)
```
 

## Other Functions

### Rollbacks
Every time `mf.run()` is called, both the existing `sys.path` list and the newly enriched `sys.path` is saved to an internal list on the `ManualFupi` instance: `mf.sys_path_history`. This allows you to rollback by overwriting `sys.path` with the backup of your choice.

For example:

```python
from fupi import ManualFupi

# create and run (or pass `autorun=True` to the constructor)
mf = ManualFupi(autorun=True)

# don't like it?
sys.path = mf.sys_path_history[0]  # Reset sys.path to pre-import state
sys.path = mf.sys_path_history[-1] # Reset sys.path to most current state
```

The sys_path_history is kept in the ManualFupi object, so if you want to rollback changes, you need to use the `from fupi import ManualFupi` import approach (or, simpy save your own sys.path snapshot).


### Shortest Path

Sometimes it's useful to know the shortest path available.  For instance, if your project source code directory is `/usr/you/dev/project/src` then fupi will add that **plus all children** to your `sys.path`.  To quickly get back to your source directory, you can use the `mf.shortest_path()` method.  This is only available with ManualFupi.

**"Shortest"** is measured in number of total directories (Path.parts), with a lexicographically (aka alphetic) tiebreaker.  

For example, assume you source directory is `./src/`

```python
from fupi import ManualFupi
mf = ManualFupi(autorun=True)

src_path = mf.shortest_path() # the `./src/` path
proj_path = src.parent #  project root
```

By default, the `shortest_path()` only includes paths that were added by fupi, however you can pass in any list of paths.  For example:

```python
from fupi import ManualFupi
mf = ManualFupi(autorun=True)

mypath = mf.shortest_path( sys.path )
```

Keep in mind, there may be "shorter" paths already in `sys.path`, so you may not get what you're expecting.   This was really added to quickly get to the "root" directory of paths added by fupi (aka your project 'root' path).

The module does expose the default `shortest_path` when run, meaning you don't need to run ManualFupi, however since the auto-run only happens once, means the `shortest_path` is only updated once.  Also note, that shortest_path is a Path object here, whereas it's a function in the ManualFupi.

```python
import fupi
src_path = fupi.shortest_path # Path to `./src/`
```

## Linters and AI Coders

The auto-load feature was designed to get down to two words for most use-cases: `import fupi` - nothing else is needed.

One minor disadvantage; linters will often see this as an unused import and flag it for removal, and/or give you a yellow squiggly underline. Or, an overly-ambitious AI coding tool may drop it without warning. If that becomes a problem, you can always print the fupi.shortest_path

 