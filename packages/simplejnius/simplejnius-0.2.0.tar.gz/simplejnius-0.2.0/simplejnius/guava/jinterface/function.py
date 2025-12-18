from jnius import PythonJavaClass, java_method

__all__ = ("Function",)


class Function(PythonJavaClass):
    """
    Java proxy for com.google.common.base.Function<F, T>.

    This wrapper lets you pass a Python callable where a Guava Function is
    expected. Only the public interface methods are implemented:
    - T apply(F)
    - boolean equals(Object)

    Usage:
        Function(lambda x: transform(x))
    """

    __javainterfaces__ = ["com/google/common/base/Function"]
    __javacontext__ = "app"

    def __init__(self, apply):
        """
        Create a Function proxy.

        Args:
            apply: A Python callable taking one argument (F) and returning a
                  value (T). It will be invoked from Java via apply.
        """
        super().__init__()
        self._apply = apply

    @java_method("(Ljava/lang/Object;)Ljava/lang/Object;")
    def apply(self, obj):
        return self._apply(obj)

    @java_method("(Ljava/lang/Object;)Z")
    def equals(self, other):
        print(other)
        if not isinstance(other, self.__class__):
            return False
        return True
