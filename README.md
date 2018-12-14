# Nifty Nesting

### Python utilities for manipulating arbitrarily nested data structures.

Includes: `flatten`, `map`, `pack_into`, `filter`, `reduce`, `assert_same_structure`

Supports `collections.Sequence` (`list`, `tuple`, etc.), `collections.Mapping` (`dict`, etc.), `namedtuple`, and `attr` data classes as part of the nesting structure.

Allows users to specify what elements should be considered part of the nesting structure and which elements should be considered "atomic" data elements via an `is_atomic` argument to all functions.

Examples:

### flatten
```python
import nifty_nesting as nest

structure = [1, (2, {'a': 3}, 4]
flat = nest.flatten(structure)
assert flat == [1, 2, 3, 4]

structure = ([1, 2], {'a': [3, 4], 'b': [5, 6]})
flat = nest.flatten(structure, is_atomic=lambda x: isinstance(x, list))
assert flat == [[1, 2], [3, 4], [5, 6]] 
```

### map
```python
import nifty_nesting as nest

structure = {'a': [1, 2], 'b': (3, 4, {'c': 5})}
mapped = nest.map(lambda x: 2*x, structure)
assert mapped == {'a': [2, 4], 'b': (6, 8, {'c': 10})}

structure = ([1, 2], {'a': [3, 4], 'b': [5, 6]})
mapped = nest.map(lambda x: max(x), structure, is_atomic=lambda x: isinstance(x, list))
assert mapped == (2, {'a': 4, 'b': 6})
```


