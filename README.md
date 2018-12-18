# Nifty Nesting

### Python utilities for manipulating arbitrarily nested data structures.

Includes: `flatten`, `map`, `pack_into`, `filter`, `reduce`, `assert_same_structure`

Heavily inspired by the [internal nesting utilities in TensorFlow.](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/util/nest.py)

### Install with 

```
pip install nifty-nesting
```

## Working with nested data is hard.

With `list`s, `tuple`s, `dict`s, `namedtuple`s, `set`s, single objects, `None`, etc., there are so many edge cases to consider. Many developers end up hacking together a solution that works only for their particular case, and becomes hard to expand in the future when a new data structure is introduced. **Don't reinvent the wheel.** `nifty-nesting` provides a set of modular utilities that can be customized to perfectly suit your project's needs.

`nifty-nesting` supports `collections.Sequence` (`list`, `tuple`, etc.), `collections.Mapping` (`dict`, etc.), `set`, `namedtuple`, and `attr` data classes as part of the nesting structure.

`nifty-nesting` allows users to specify what elements should be considered part of the nesting structure and which elements should be considered "atomic" data elements via an `is_atomic` argument to all functions.

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

## Documentation

### Main functions

#### flatten(structure, is_atomic=is_scalar)
    
    Returns a flattened list containing the atomic elements of `structure`.

    The elements of `structure` are flattened in a deterministic order.

    ```
    import nifty_nesting as nest
    flat = nest.flatten([1, (2, {'a': 3}, 4])
    assert flat == [1, 2, 3, 4]
    ```

    Arguments:
        structure: An arbitrarily nested structure of elements.
        is_atomic: A function that returns `True` if a certain element
          of `structure` ought to be treated as an atomic element, i.e.
          not as part of the nesting structure.

    Returns:
        A list containing every atomic element of `structure`.
    
#### map(func, structure, is_atomic=is_scalar)
    Maps the atomic elements of `structure`.

    ```
    import nifty_nesting as nest
    structure = {'a': [1, 2], 'b': (3, 4, {'c': 5})}
    mapped = nest.map(lambda x: 2*x, structure)
    assert mapped == {'a': [2, 4], 'b': (6, 8, {'c': 10})}
    ```

    Arguments:
      func: The function to use to map atomic elements of `structure`.
      structure: An arbitrarily nested structure of elements.
      is_atomic: A function that returns `True` if a certain element
        of `structure` ought to be treated as an atomic element, i.e.
        not as part of the nesting structure.

    Returns:
      A structure with the same structure as `structure`, with the atomic elements
        mapped according to `func`.
    
#### reduce(func, structure, is_atomic=is_scalar):
    Reduces the atomic elements of `structure`.

    ```
    import nifty_nesting as nest
    structure = {'a': [1, 2], 'b': (3, 4, {'c': 5})}
    reduced = nest.reduce(lambda x, y: x+y, structure)
    assert reduced == 15
    ```

    Arguments:
      func: The function to use to reduce atomic elements of `structure`.
      structure: An arbitrarily nested structure of elements.
      is_atomic: A function that returns `True` if a certain element
        of `structure` ought to be treated as an atomic element, i.e.
        not as part of the nesting structure.

    Returns:
      The reduced value.
    
 #### filter(func, structure, keep_structure=True, is_atomic=is_scalar)
    Filters the atomic elements of `structure`.

    ```
    import nifty_nesting as nest
    structure = {'a': [1, 2], 'b': (3, 4, {'c': 5})}
    filtered = nest.filter(lambda x: x > 2, structure)
    assert filtered == {'a': [], 'b': (3, 4, {'c': 5})}

    filtered = nest.filter(lambda x: x > 2, structure, keep_structure=False)
    assert filtered == {'b': (3, 4, {'c': 5})}
    ```

    Arguments:
      func: The function to use to filter atomic elements of `structure`.
      structure: An arbitrarily nested structure of elements.
      keep_structure: Whether or not to preserve empty substructures. If
        `True`, these structures will be kept. If `False`, they will be
        entirely filtered out.
      is_atomic: A function that returns `True` if a certain element
        of `structure` ought to be treated as an atomic element, i.e.
        not as part of the nesting structure.

    Returns:
      The filtered elements of `structure` in the same structure as `structure`.
      
 #### assert_same_structure(structure1, structure2, is_atomic=is_scalar)
    Asserts that `structure1` and `structure2` have the same nested structure.

    ```
    import nifty_nesting as nest
    structure1 = {'a': [1, 2], 'b': (3, 4, {'c': 5})}
    structure1 = {'a': ['a', 'b'], 'b': ('c', 'd', {'c': 'e'})}
    nest.assert_same_structure(structure1, structure2)
    ```

    Arguments:
      structure1: An arbitrarily nested structure of elements.
      structure2: An arbitrarily nested structure of elements.
      is_atomic: A function that returns `True` if a certain element
        of `structure` ought to be treated as an atomic element, i.e.
        not as part of the nesting structure.

    Raises:
      `AssertionError` if the structures are not the same.
    
#### pack_list_into(structure, flat_list, is_atomic=is_scalar)
    Packs the atomic elements of `flat_list` into the same structure as `structure`.

    ``
    import nifty_nesting as nest
    structure = {'a': [1, 2], 'b': (3, 4, {'c': 5})}
    flat_list = [2, 4, 6, 7, 10]
    packed = nest.pack_list_into(structure, flat_list)
    assert packed == {'a': [2, 4], 'b': (6, 8, {'c': 10})}
    ```

    Arguments:
      structure: An arbitrarily nested structure of elements.
      flat_list: A flat list with the same number of atomic elements as
        `structure`.
      is_atomic: A function that returns `True` if a certain element
        of `structure` ought to be treated as an atomic element, i.e.
        not as part of the nesting structure.

    Returns:
      A structure with the atomic elements of `flat_list` packed into the same
        structure as `structure`.

### Helper functions for `is_atomic` 
 
 #### is_scalar(element)
    An `is_atomic` criterion. Returns `True` for scalar elements.

    Scalar elements are : strings and any object that is not one of:
      collections.Sequence, collections.Mapping, set, or attrs object.

    ```
    import nifty_nesting as nest
    flat = nest.flatten([1, [2, 3]], is_atomic=is_scalar)
    assert flat == [1, 2, 3]
    ```

    Arguments:
      element: The element to check.

    Returns:
      `True` if the element is a scalar, else `False`.
    
#### has_max_depth(depth, is_atomic=is_scalar)
    Returns an `is_atomic` criterion that checks the depth of a structure.

    This function returns a function that can be passed to `is_atomic` to
    preserve all structures up to a given depth.

    ```
    import nifty_nesting as nest
    flat = nest.flatten([[1, 2], [3, [4, 5]]], is_atomic=has_max_depth(1))
    assert flat == [[1, 2], [3], [4, 5]]
    ```

    Arguments:
      depth: The maximum depth a structure can have in order to be considered
        as an atomic element. For instance, `[1, 2, {'a': 3}]` has a depth of 2.
        is_atomic: A function that returns `True` if a certain element
          of `structure` ought to be treated as an atomic element, i.e.
          not as part of the nesting structure.

    Returns:
       A function that can be passed to `is_atomic` to check for elements
       with a depth of `depth` or less.

#### is_sequence(element)
    
Returns `True` for instances of `collections.Sequence`.

#### is_mapping(element)
   
Returns `True` for instances of `collections.Mapping`.

#### is_set(element)

 Returns `True` for instances of `set`.
 
 #### is_namedtuple(element)
 
 Returns `True` for instances of `namedtuple`.
 
 #### is_attrs_object(element)
   
 Returns `True` for instances of `attr`-decorated classes.









           
           
