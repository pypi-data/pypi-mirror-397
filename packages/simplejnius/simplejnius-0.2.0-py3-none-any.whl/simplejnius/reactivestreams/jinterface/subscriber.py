from jnius import PythonJavaClass, java_method

__all__ = ("Subscriber",)


class Subscriber(PythonJavaClass):
    __javainterfaces__ = ["org/reactivestreams/Subscriber"]
    __javacontext__ = "app"

    def __init__(self, callback: dict):
        self.callback = callback

    def _callback(self, name, *args):
        func = self.callback.get(name)
        if func:
            return func(*args)

    @java_method("(Lorg/reactivestreams/Subscription;)V")
    def onSubscribe(self, subscription):
        self._callback("on_subscribe", subscription)

    @java_method("(Ljava/lang/Object;)V")
    def onNext(self, obj):
        self._callback("on_next", obj)

    @java_method("(Ljava/lang/Throwable;)V")
    def onError(self, throwable):
        self._callback("on_error", throwable)

    @java_method("()V")
    def onComplete(self):
        self._callback("on_complete")
