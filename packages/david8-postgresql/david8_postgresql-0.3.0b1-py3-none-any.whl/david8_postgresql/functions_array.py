from .core.functions_array_factory import Col2AnyArgsFactory as _Col2AnyArgsFactory
from .core.functions_array_factory import StrSeparatedArgsFactory as _StrSeparatedArgsFactory

unnest = _StrSeparatedArgsFactory(name='unnest')
array_remove = _Col2AnyArgsFactory(name='array_remove')
