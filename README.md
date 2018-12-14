# Nifty Nesting

### Python utilities for manipulating arbitrarily nested data structures.

Includes: `flatten`, `map`, `pack_into`, `filter`, `reduce`, `assert_same_structure`

Supports `collections.Sequence` (`list`, `tuple`, etc.), `collections.Mapping` (`dict`, etc.), `set`, `namedtuple`, and `attr` data classes as part of the nesting structure.

Allows users to specify what elements should be considered part of the nesting structure and which elements should be considered "atomic" data elements via an `is_atomic` argument to all functions.

Examples:

### flatten

Returns a list containing every atomic element of a nested structure. Elements are returned in a determinstic order.

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

Maps every atomic element of a nested structure.

```python
import nifty_nesting as nest

structure = {'a': [1, 2], 'b': (3, 4, {'c': 5})}
mapped = nest.map(lambda x: 2*x, structure)
assert mapped == {'a': [2, 4], 'b': (6, 8, {'c': 10})}

structure = ([1, 2], {'a': [3, 4], 'b': [5, 6]})
mapped = nest.map(lambda x: max(x), structure, is_atomic=lambda x: isinstance(x, list))
assert mapped == (2, {'a': 4, 'b': 6})
```

### pack_list_into

Packs a flat list into any arbitrary structure with the same number of atomic elements. Elements are packed in a deterministic order that is compatible with flat lists created by `flatten`.

```python
import nifty_nesting as nest

structure = (1, {'key': [2, {3, 4}, 5]}, [6, 7])
flat_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
packed = nest.pack_list_into(structure, flat_list)
assert packed == ('a', {'key': ['b', {'c', 'd'}, 'e']}, ['f', 'g'])
```

### End-to-End Example
```python
from collections import namedtuple
import nifty_nesting as nest

Person = namedtuple('Person', ['name', 'birthday'])

people = ({'user': Person('John', '12/11'),
           'friends': [
              Person('Jim', '12/12'),
              Person('Tim', '12/13'),
              Person('Suzy', 12/14'),
           ],
           'family': {
             'Mom': Person('Mary', '12/15'),
             'Dad': Person('Michael', '12/16')
           }},
           {'user': Person('Bob', '12/17'),
           'friends': [
              Person('Tony', '12/18'),
              Person('Rick', '12/19'),
              Person('Kelly', 12/20'),
           ],
           'family': {
             'Mom': Person('Fred', '12/21'),
             'Dad': Person('Judith', '12/22')
           }})
messages_list = []
for person in nest.flatten(people, is_atomic=lambda x: isinstance(x, Person)):
  if person['birthday'] == today():
    messages_list.append('Happy Birthday {}!'.format(person['name'])
  else:
    messages_list.append('{} days til your Birthday'.format(person['birthday' - today()))
messages = nest.pack_list_into(people, 
                               messages_list, 
                               is_atomic=lambda x: isinstance(x, Person))
```
                            


           
           
