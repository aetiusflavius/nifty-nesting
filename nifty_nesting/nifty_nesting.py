"""Python utilities for manipulating arbitrarily nested data structures."""
import collections
import six

# pylint: disable=line-too-long
# pylint: disable=redefined-builtin

# Capture built-in
_map = map
_filter = filter


def is_sequence(element):
    """Returns `True` for instances of `collections.Sequence`."""
    return isinstance(element, collections.Sequence)


def is_mapping(element):
    """Returns `True` for instances of `collections.Mapping`."""
    return isinstance(element, collections.Mapping)


def is_set(element):
    """Returns `True` for instances of `set`."""
    return isinstance(element, set)


def is_namedtuple(element):
    """Returns `True` for instances of `namedtuple`."""
    bases = type(element).__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(element, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    if all(isinstance(field, six.string_types) for field in fields):
        return True
    return False


def is_attrs_object(element):
    """Returns `True` for instances of `attr`-decorated classes."""
    return (hasattr(element, '__class__')
            and hasattr(element.__class__, '__attrs_attrs__'))


def is_scalar(element):
    """An `is_atomic` criterion. Returns `True` for scalar elements.

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
    """
    if isinstance(element, six.string_types):
        return True
    if is_attrs_object(element):
        return False
    if is_sequence(element) or is_set(element):
        return False
    if is_mapping(element):
        return False
    return True


def has_max_depth(depth, is_atomic=is_scalar):
    """Returns an `is_atomic` criterion that checks the depth of a structure.

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
    """
    def _has_max_depth(structure):
        def _has_max_depth_helper(structure, _depth):
            if is_atomic(structure):
                return _depth
            return max([_has_max_depth_helper(substructure, _depth+1)
                        for substructure in _shallow_yield_from(structure, is_atomic)])

        _depth = _has_max_depth_helper(structure, 0)
        return _depth <= depth

    return _has_max_depth


def flatten(structure, is_atomic=is_scalar):
    """Returns a flattened list containing the atomic elements of `structure`.

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
    """
    def _flatten_helper(structure, is_atomic, flat_list):
        if structure is None:
            return

        if is_atomic(structure):
            flat_list.append(structure)
        elif is_attrs_object(structure):
            for substructure in _iter_attrs(structure):
                _flatten_helper(substructure, is_atomic, flat_list)
        elif is_sequence(structure) or is_set(structure):
            for substructure in structure:
                _flatten_helper(substructure, is_atomic, flat_list)
        elif is_mapping(structure):
            for key in sorted(six.iterkeys(structure)):
                _flatten_helper(structure[key], is_atomic, flat_list)
        else:
            raise ValueError(
                'Encountered an element that was neither atomic nor a structure: {}'.format(structure))

    flat_list = []
    _flatten_helper(structure, is_atomic, flat_list)
    return flat_list


def map(func, structure, is_atomic=is_scalar):
    """Maps the atomic elements of `structure`.

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
    """
    if structure is None:
        return None

    if is_atomic(structure):
        return func(structure)

    if is_attrs_object(structure):
        mapped = [map(func, substructure, is_atomic) for substructure in _iter_attrs(structure)]
        return _shallow_structure_like(structure, mapped, is_atomic)

    if is_sequence(structure) or is_set(structure):
        mapped = [map(func, substructure, is_atomic) for substructure in structure]
        return _shallow_structure_like(structure, mapped, is_atomic)


    if is_mapping(structure):
        mapped = [map(func, structure[key], is_atomic) for key in _sorted_keys(structure)]
        return _shallow_structure_like(structure, mapped, is_atomic)

    raise ValueError(
        'Encountered an element that was neither atomic nor a structure: {}'.format(structure))


def reduce(func, structure, is_atomic=is_scalar):
    """Reduces the atomic elements of `structure`.

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
    """
    if structure is None:
        return None

    for i, element in enumerate(flatten(structure, is_atomic)):
        if i == 0:
            reduced = element
        else:
            reduced = func(reduced, element)
    return reduced


def filter(func, structure, keep_structure=True, is_atomic=is_scalar):
    """Filters the atomic elements of `structure`.

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
    """
    class FALSEY:
        """Used as a placeholder for values we want to filter out."""
        pass

    # A value to be used to determine if this element should be filtered away.
    def _filter_helper(func, structure, is_atomic, keep_structure):

        if structure is None:
            return FALSEY

        if is_atomic(structure):
            if func(structure):
                return structure
            return FALSEY

        # Fields that evaluate to false are set to `None`.
        # There's not really a better option for these data structures.
        if is_attrs_object(structure) or is_namedtuple(structure):
            filtered_list = []
            for substructure in _shallow_yield_from(structure):
                filtered_list.append(_filter_helper(func, substructure, is_atomic, keep_structure))
            if keep_structure or not all(element is FALSEY for element in filtered_list):
                filtered_list = _map(lambda x: None if x is FALSEY else x, filtered_list)
                return _shallow_structure_like(structure, filtered_list)
            return FALSEY

        # Filter out elements that evaluate to false.
        if is_sequence(structure) or is_set(structure):
            filtered_list = []
            for substructure in _shallow_yield_from(structure):
                filtered_substructure = _filter_helper(func, substructure, is_atomic, keep_structure)
                if filtered_substructure is not FALSEY:
                    filtered_list.append(filtered_substructure)
            # If not `keep_structures`, don't return empty structures.
            if keep_structure or filtered_list:
                return _shallow_structure_like(structure, filtered_list)
            return FALSEY

        # Filter out elements that evaluate to false, keep track of keys.
        if is_mapping(structure):
            filtered_dict = {}
            for key in _sorted_keys(structure):
                substructure = structure[key]
                filtered_substructure = _filter_helper(func, substructure, is_atomic, keep_structure)
                if filtered_substructure is not FALSEY:
                    filtered_dict[key] = filtered_substructure
            if keep_structure or filtered_dict:
                return _shallow_structure_like(structure, filtered_dict)
            return FALSEY

    filtered_structure = _filter_helper(func, structure, is_atomic, keep_structure)
    if filtered_structure is FALSEY:
        return None
    else:
        return filtered_structure


def assert_same_structure(structure1, structure2, is_atomic=is_scalar):
    """Asserts that `structure1` and `structure2` have the same nested structure.

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
    """
    assert is_atomic(structure1) == is_atomic(structure2)
    if not is_atomic(structure1):
        # Only check the types for elements that are part of the structure.
        assert type(structure1) == type(structure2)

        if is_mapping(structure1):
            assert _sorted_keys(structure1) == _sorted_keys(structure2)

        substructures1 = list(_shallow_yield_from(structure1, is_atomic))
        substructures2 = list(_shallow_yield_from(structure2, is_atomic))
        # Zip will silently ignore a longer list.
        assert len(substructures1) == len(substructures2)
        for substructure1, substructure2 in zip(substructures1, substructures2):
            assert_same_structure(substructure1, substructure2, is_atomic)


def pack_list_into(structure, flat_list, is_atomic=is_scalar):
    """Packs the atomic elements of `flat_list` into the same structure as `structure`.

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
    """
    if structure is None:
        return None

    def _pack_into_helper(structure, flat_list, is_atomic, index):
        packed_list = []
        for substructure in _shallow_yield_from(structure, is_atomic):
            if is_atomic(substructure):
                packed_list.append(flat_list[index])
                index += 1
            else:
                index, packed_substructure = _pack_into_helper(substructure, flat_list, is_atomic, index)
                packed_list.append(packed_substructure)
        packed_structure = _shallow_structure_like(structure, packed_list, is_atomic)
        return index, packed_structure

    _, packed_structure = _pack_into_helper(structure, flat_list, is_atomic, 0)
    return packed_structure


def _shallow_structure_like(structure, elements, is_atomic=is_scalar):
    if structure is None:
        return None

    if is_atomic(structure):
        return elements[0]

    if is_namedtuple(structure) or is_attrs_object(structure):
        return type(structure)(*elements)

    if is_sequence(structure) or is_set(structure):
        return type(structure)(elements)

    if is_mapping(structure):
        # If a Mapping is passed for `elements`, `elements` can have different keys
        # than `structure`. Otherwise, the keys are assumed to be the same.
        if not is_mapping(elements):
            elements = dict(zip(_sorted_keys(structure), elements))
        return type(structure)((key, elements[key]) for key in _sorted_keys(elements))


def _sorted_keys(mapping):
    try:
        return sorted(six.iterkeys(mapping))
    except TypeError:
        raise ValueError('dicts with unsortable keys are not supported, found: {}'.format(mapping))


def _iter_attrs(element):
    return [getattr(element, attr.name)
            for attr in
            getattr(element.__class__, '__attrs_attrs__')]


def _shallow_yield_from(structure, is_atomic=is_scalar):
    if is_atomic(structure):
        yield structure
    elif is_mapping(structure):
        for key in _sorted_keys(structure):
            yield structure[key]
    elif is_attrs_object(structure):
        for substructure in _iter_attrs(structure):
            yield substructure
    else:
        for substructure in structure:
            yield substructure

# pylint: enable=line-too-long
# pylint: enable=redefined-builtin
