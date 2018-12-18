from .nifty_nesting import assert_same_structure
from .nifty_nesting import filter
from .nifty_nesting import flatten
from .nifty_nesting import has_max_depth
from .nifty_nesting import is_attrs_object
from .nifty_nesting import is_mapping
from .nifty_nesting import is_namedtuple
from .nifty_nesting import is_scalar
from .nifty_nesting import is_sequence
from .nifty_nesting import is_set
from .nifty_nesting import map
from .nifty_nesting import pack_list_into
from .nifty_nesting import reduce

name = 'nifty_nesting'

__all__ = ['assert_same_structure',
           'filter',
           'flatten',
           'has_max_depth',
           'is_attrs_object',
           'is_mapping',
           'is_namedtuple',
           'is_scalar',
           'is_set',
           'is_sequence',
           'map',
           'pack_list_into',
           'reduce']
