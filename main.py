import inspect

from typing import Any, Dict, Optional, Type

# equivalent of Django Queryset
class Parent:
    def parent_and_child_method(self) -> str:
        return 'parent and child method'

# Think about this as Django Manager class for now
class Child:
    def child_only_method(self) -> str:
        return 'child only method'

    @classmethod
    def _get_parent_methods(cls, parent_class: type) -> Dict[str, Any]:
        def create_method(name, method):
            def child_method(self, *args, **kwargs):
                return getattr(self.get_parent(), name)(*args, **kwargs)
            child_method.__name__ = method.__name__
            child_method.__doc__ = method.__doc__
            return child_method

        new_methods = {}
        for name, method in inspect.getmembers(parent_class, predicate=inspect.isfunction):
            # Only copy missing methods.
            if hasattr(cls, name):
                continue
            # Copy the method onto the child.
            new_methods[name] = create_method(name, method)
        return new_methods

    @classmethod
    def from_parent(cls, parent_class: Type[Parent], class_name: Optional[str] = None) -> Any:
        if class_name is None:
            class_name = '%sFrom%s' % (cls.__name__, parent_class.__name__)
        class_dict = {
            '_parent_class': parent_class,
        }
        class_dict.update(cls._get_parent_methods(parent_class))
        return type(class_name, (cls,), class_dict)
    
    def get_parent(self):
        return self._parent_class()

ChildFromParent = Child.from_parent(Parent)

class Uncle:
    nephew = ChildFromParent()

#reveal_type(Uncle.nephew)
#revelal_type(Uncle.nephew.child_only_method())
