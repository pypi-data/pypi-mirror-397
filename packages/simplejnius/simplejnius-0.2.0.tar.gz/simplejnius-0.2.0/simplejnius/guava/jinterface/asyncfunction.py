from jnius import PythonJavaClass, java_method

__all__ = ("AsyncFunction",)


class AsyncFunction(PythonJavaClass):
    """
    Java proxy for com.google.common.util.concurrent.AsyncFunction<F, T>.

    This wrapper lets you pass a Python callable where a Guava Function is
    expected. Only the public interface methods are implemented:
    - T apply(F)

    Usage:
        Function(lambda x: transform(x))
    """

    __javainterfaces__ = ["com/google/common/util/concurrent/AsyncFunction"]
    __javacontext__ = "app"

    def __init__(self, apply):
        """
        Create a AsyncFunction proxy.

        Args:
            apply: A Python callable taking one argument (F) and returning a
                  value (T). It will be invoked from Java via apply.
        """
        super().__init__()
        self._apply = apply

    @java_method("(Ljava/lang/Object;)Lcom/google/common/util/concurrent/ListenableFuture;")
    def apply(self, obj):
        return self._apply(obj)
