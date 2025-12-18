from jnius import PythonJavaClass, java_method

__all__ = ("FutureCallback",)


class FutureCallback(PythonJavaClass):
    __javainterfaces__ = ["com/google/common/util/concurrent/FutureCallback"]
    __javacontext__ = "app"

    def __init__(self, on_success, on_failure):
        self.on_success = on_success
        self.on_failure = on_failure

    @java_method("(Ljava/lang/Object;)V")
    def onSuccess(self, obj):
        self.on_success(obj)

    @java_method("(Ljava/lang/Throwable;)V")
    def onFailure(self, throwable):
        self.on_failure(throwable)
