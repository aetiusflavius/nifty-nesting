import collections
import six

# Capture built-in
_map = map
_filter = filter

def is_sequence(element):
    return isinstance(element, collections.Sequence)


def is_mapping(element):
    return isinstance(element, collections.Mapping)


def is_set(element):
    return isinstance(element, set)


def is_namedtuple(element):
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
    return (hasattr(element, '__class__')
            and hasattr(element.__class__, '__attrs_attrs__'))

def is_scalar(element):
    if isinstance(element, six.string_types):
        return True
    if is_attrs_object(element):
        return False
    if is_sequence(element) or is_set(element):
        return False
    if is_mapping(element):
        return False
    return True

class has_depth:
    def __init__(self, depth, is_leaf=is_scalar):
        self.depth = depth
        self.is_leaf = is_leaf

    def __call__(self, structure):
        depth = self._depth_helper(structure, 0)
        return depth == self.depth

    def _depth_helper(self, structure, depth):
        if self.is_leaf(structure):
            return depth

        return max([self._depth_helper(substructure, depth+1)
                    for substructure in _shallow_yield_from(structure)])


def flatten(structure, is_atomic=is_scalar):
    """Returns a flattened list containing the atomic elements of `structure`.

    The elements of `structure` are flattened in a deterministic order.

    Arguments:
        structure: An arbitrarily nested structure of elements.
        is_atomic: A function that returns `True` if a certain element
          of `structure` ought to be treated as an atomic element, i.e.
          not as part of the nesting structure. By default, this is

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
    if structure is None:
        return None

    if is_atomic(structure):
        return func(structure)

    if is_sequence(structure) or is_set(structure) or is_attrs_object(structure):
        mapped = [map(func, substructure, is_atomic) for substructure in structure]
        return _shallow_structure_like(structure, mapped, is_atomic)

    if is_mapping(structure):
        mapped = [map(func, structure[key], is_atomic) for key in _sorted_keys(structure)]
        return _shallow_structure_like(structure, mapped, is_atomic)

    raise ValueError(
        'Encountered an element that was neither atomic nor a structure: {}'.format(structure))


def reduce(func, structure):
    if structure is None:
        return None

    for i, element in enumerate(flatten(structure)):
        if i == 0:
            reduced = element
        else:
            reduced = func(reduced, element)
    return reduced



def filter(func, structure, is_atomic=is_scalar, keep_structure=True):
    class FALSEY:
        pass

    # A value to be used to determine if this element should be filtered away.
    def _filter_helper(func, structure, is_atomic, keep_structure):

        if structure is None:
            return FALSEY

        if is_atomic(structure):
            if func(structure):
                return structure
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
            else:
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
            else:
                return FALSEY

        # Fields that evaluate to false are set to `None`. 
        if is_attrs_object(structure):
            filtered_list = []
            for substructure in _iter_attrs(structure):
                filtered_list.append(_filter_helper(func, substructure, is_atomic, keep_structure))
            if keep_structure or not all(element is FALSEY for element in filtered_list):
                filtered_list = _map(lambda x: None if x is FALSEY else x, filtered_list)
                return _shallow_structure_like(structure, filtered_list)
            else:
                return FALSEY

    filtered_structure = _filter_helper(func, structure, is_atomic, keep_structure)
    if filtered_structure is FALSEY:
        # Should this return some other value? `None`?
        return []
    else:
        return filtered_structure
        

def assert_same_structure(structure1, structure2, is_atomic=is_scalar):
    assert is_atomic(structure1) == is_atomic(structure2)
    if not is_atomic(structure1):
        # Only check the types for elements that are part of the structure.
        assert type(structure1) == type(structure2)

        if is_mapping(structure1):
            assert _sorted_keys(structure1) == _sorted_keys(structure2)

        substructures1 = list(_shallow_yield_from(structure1))
        substructures2 = list(_shallow_yield_from(structure2))
        # Zip will silently ignore a longer list.
        assert len(substructures1) == len(substructures2)
        for substructure1, substructure2 in zip(substructures1, substructures2):
            assert_same_structure(substructure1, substructure2, is_atomic=is_scalar)


def pack_into(structure, flat_list, is_atomic=is_scalar):
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
        if is_mapping(elements):
            elements = dict(zip(_sorted_keys(structure), elements))
        return type(structure)((key, result[key]) for key in _sorted_keys(elements))


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
