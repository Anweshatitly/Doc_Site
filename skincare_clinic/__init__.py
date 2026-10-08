"""
skincare_clinic project package.
Includes Python 3.14+ compatibility patch for Django Template BaseContext.__copy__.
"""
import sys

# Python 3.14+ compatibility fix for Django Template Context copy
if sys.version_info >= (3, 14):
    try:
        from django.template import context as _ctx

        def _patched_base_context_copy(self):
            obj = object.__new__(self.__class__)
            obj.__dict__.update(self.__dict__)
            obj.dicts = self.dicts[:]
            return obj

        _ctx.BaseContext.__copy__ = _patched_base_context_copy
    except ImportError:
        pass
