"""
Python binding for the Google Guava Futures class.

This module provides a PyJNIus binding for the com.google.common.util.concurrent.Futures Java class.
It allows Python code to interact with Google Guava's futures utilities, which provide various
helper methods for working with ListenableFuture instances and other concurrent programming tools.

The Futures class offers methods for creating, transforming, and combining futures, as well as
utilities for handling callbacks, timeouts, and error conditions.
"""

from jnius import JavaClass, MetaJavaClass, JavaMultipleMethod, JavaStaticMethod

__all__ = ("Futures",)


class Futures(JavaClass, metaclass=MetaJavaClass):
    """
    Python binding for the com.google.common.util.concurrent.Futures Java class.
    
    This class provides utility methods for working with ListenableFuture instances and
    other concurrent programming tools from the Google Guava library. It includes methods for:
    
    - Creating immediate futures with predefined values or states
    - Submitting tasks to executors and obtaining futures
    - Transforming future results
    - Handling errors and exceptions
    - Combining multiple futures
    - Managing timeouts and cancellation
    - Retrieving future results safely
    """
    __javaclass__ = 'com/google/common/util/concurrent/Futures'

    immediateFuture = JavaStaticMethod(
        '(Ljava/lang/Object;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a ListenableFuture which has its value set immediately upon construction.
    
    The returned ListenableFuture is already in the completed state, so listeners
    added to it will be called immediately.
    
    Parameters:
        value: The value to be returned by the future.
        
    Returns:
        A ListenableFuture which is already completed with the given value.
    """

    immediateVoidFuture = JavaStaticMethod(
        '()Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a successful ListenableFuture containing null.
    
    The returned ListenableFuture is already in the completed state, so listeners
    added to it will be called immediately.
    
    Returns:
        A ListenableFuture which is already completed with the null value.
    """

    immediateFailedFuture = JavaStaticMethod(
        '(Ljava/lang/Throwable;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a ListenableFuture which has an exception set immediately upon construction.
    
    The returned ListenableFuture is already in the completed state with the given
    exception, so listeners added to it will be called immediately.
    
    Parameters:
        throwable: The exception to be set as the cause of failure.
        
    Returns:
        A ListenableFuture which is already completed with the given exception.
    """

    immediateCancelledFuture = JavaStaticMethod(
        '()Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a ListenableFuture which is cancelled immediately upon construction.
    
    The returned ListenableFuture is already in the cancelled state, so listeners
    added to it will be called immediately.
    
    Returns:
        A ListenableFuture which is already cancelled.
    """

    submit = JavaMultipleMethod([
        (
            '(Ljava/util/concurrent/Callable;'
            'Ljava/util/concurrent/Executor;)'
            'Lcom/google/common/util/concurrent/ListenableFuture;',
            True, False
        ),
        (
            '(Ljava/lang/Runnable;'
            'Ljava/util/concurrent/Executor;)'
            'Lcom/google/common/util/concurrent/ListenableFuture;',
            True, False
        )
    ])
    """
    Submits a task for execution on the given executor and returns a ListenableFuture.
    
    This method is a convenience wrapper for creating a ListenableFuture from a Callable
    or Runnable and submitting it to an executor.
    
    Overloaded methods:
    1. submit(callable, executor): Submits a Callable task for execution and returns a future.
    2. submit(runnable, executor): Submits a Runnable task for execution and returns a future.
    
    Parameters:
        callable: The Callable task to execute.
        runnable: The Runnable task to execute.
        executor: The executor to which the task will be submitted.
        
    Returns:
        A ListenableFuture representing the result of the task.
    """

    submitAsync = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/AsyncCallable;'
        'Ljava/util/concurrent/Executor;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Submits an AsyncCallable task for execution on the given executor and returns a ListenableFuture.
    
    An AsyncCallable is a task that returns a ListenableFuture rather than a direct result.
    This method is useful for chaining asynchronous operations.
    
    Parameters:
        callable: The AsyncCallable task to execute.
        executor: The executor to which the task will be submitted.
        
    Returns:
        A ListenableFuture representing the result of the AsyncCallable's future.
    """

    scheduleAsync = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/AsyncCallable;'
        'JLjava/util/concurrent/TimeUnit;'
        'Ljava/util/concurrent/ScheduledExecutorService;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Schedules an AsyncCallable task for execution after a delay and returns a ListenableFuture.
    
    This method is similar to submitAsync but allows scheduling the task to run after
    a specified delay.
    
    Parameters:
        callable: The AsyncCallable task to execute.
        delay: The time to delay execution.
        unit: The time unit of the delay parameter.
        executor: The scheduled executor service to which the task will be submitted.
        
    Returns:
        A ListenableFuture representing the result of the AsyncCallable's future.
    """

    catching = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/ListenableFuture;'
        'Ljava/lang/Class;Lcom/google/common/base/Function;'
        'Ljava/util/concurrent/Executor;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a future that catches a specific exception type from the input future.
    
    If the input future fails with the specified exception type, the returned future will
    instead be completed with the result of applying the provided function to the exception.
    
    Parameters:
        input: The input ListenableFuture.
        exceptionType: The exception type to catch.
        fallback: A Function that maps from the exception to the fallback output.
        executor: The executor to run the fallback function.
        
    Returns:
        A ListenableFuture that will be completed with either the result of the input future
        or the result of the fallback function if the input fails with the expected exception type.
    """

    catchingAsync = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/ListenableFuture;'
        'Ljava/lang/Class;'
        'Lcom/google/common/util/concurrent/AsyncFunction;'
        'Ljava/util/concurrent/Executor;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a future that catches a specific exception type from the input future asynchronously.
    
    If the input future fails with the specified exception type, the returned future will
    instead be completed with the result of applying the provided async function to the exception.
    This is similar to catching() but allows the fallback function to return a future.
    
    Parameters:
        input: The input ListenableFuture.
        exceptionType: The exception type to catch.
        fallback: An AsyncFunction that maps from the exception to a ListenableFuture.
        executor: The executor to run the fallback function.
        
    Returns:
        A ListenableFuture that will be completed with either the result of the input future
        or the result of the fallback function's future if the input fails with the expected exception type.
    """

    withTimeout = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/ListenableFuture;'
        'JLjava/util/concurrent/TimeUnit;'
        'Ljava/util/concurrent/ScheduledExecutorService;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a future that is equivalent to the input but with a timeout applied.
    
    If the input future does not complete before the timeout, the returned future will
    be cancelled and throw a TimeoutException.
    
    Parameters:
        input: The input ListenableFuture.
        timeout: The maximum time to wait.
        unit: The time unit of the timeout parameter.
        scheduledExecutor: The executor to use to schedule the timeout.
        
    Returns:
        A ListenableFuture that will complete with the same result as the input future
        or will be cancelled and throw a TimeoutException if the timeout is reached.
    """

    transformAsync = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/ListenableFuture;'
        'Lcom/google/common/util/concurrent/AsyncFunction;'
        'Ljava/util/concurrent/Executor;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a new ListenableFuture whose result is asynchronously derived from the result of the input future.
    
    If the input future succeeds, the returned future will be completed with the result of
    applying the provided async function to the input's result. If the function itself throws
    an exception, the returned future will fail with that exception.
    
    Parameters:
        input: The input ListenableFuture.
        function: An AsyncFunction to transform the result of the input future to a new future.
        executor: The executor to run the function.
        
    Returns:
        A ListenableFuture that holds the result of the function's future.
    """

    transform = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/ListenableFuture;'
        'Lcom/google/common/base/Function;'
        'Ljava/util/concurrent/Executor;)'
        'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a new ListenableFuture whose result is derived from the result of the input future.
    
    If the input future succeeds, the returned future will be completed with the result of
    applying the provided function to the input's result. If the function itself throws
    an exception, the returned future will fail with that exception.
    
    Parameters:
        input: The input ListenableFuture.
        function: A Function to transform the result of the input future.
        executor: The executor to run the function.
        
    Returns:
        A ListenableFuture that holds the result of the transformation.
    """

    lazyTransform = JavaStaticMethod(
        '(Ljava/util/concurrent/Future;'
        'Lcom/google/common/base/Function;)'
        'Ljava/util/concurrent/Future;'
    )
    """
    Returns a Future whose result is derived from the result of the input future.
    
    Unlike transform(), this method does not execute the transformation until the result
    is actually requested. This is useful when the transformation is expensive and might
    not be needed.
    
    Parameters:
        input: The input Future.
        function: A Function to transform the result of the input future.
        
    Returns:
        A Future that lazily applies the transformation when its result is requested.
    """

    allAsList = JavaMultipleMethod([
        (
            '([Lcom/google/common/util/concurrent/ListenableFuture;)'
            'Lcom/google/common/util/concurrent/ListenableFuture;',
            True, False
        ),
        (
            '(Ljava/lang/Iterable;)'
            'Lcom/google/common/util/concurrent/ListenableFuture;',
            True, False
        )
    ])
    """
    Returns a ListenableFuture that succeeds when all input futures succeed.
    
    The returned future succeeds with a list of the results of all input futures when
    all input futures succeed. If any input future fails or is cancelled, the returned
    future fails or is cancelled with the same cause.
    
    Overloaded methods:
    1. allAsList(futures...): Takes a varargs array of ListenableFuture instances.
    2. allAsList(futures): Takes an Iterable of ListenableFuture instances.
    
    Parameters:
        futures: The input futures to combine.
        
    Returns:
        A ListenableFuture containing a list of the results of all input futures.
    """

    whenAllComplete = JavaMultipleMethod([
        (
            '([Lcom/google/common/util/concurrent/ListenableFuture;)'
            'Lcom/google/common/util/concurrent/Futures$FutureCombiner;',
            True, False
        ),
        (
            '(Ljava/lang/Iterable;)'
            'Lcom/google/common/util/concurrent/Futures$FutureCombiner;',
            True, False
        )
    ])
    """
    Returns a FutureCombiner that can be used to combine futures after all input futures complete.
    
    The returned combiner can be used to create a derived future that executes a function
    when all input futures complete, regardless of whether they succeed or fail.
    
    Overloaded methods:
    1. whenAllComplete(futures...): Takes a varargs array of ListenableFuture instances.
    2. whenAllComplete(futures): Takes an Iterable of ListenableFuture instances.
    
    Parameters:
        futures: The input futures to monitor for completion.
        
    Returns:
        A FutureCombiner that can be used to create a derived future.
    """

    whenAllSucceed = JavaMultipleMethod([
        (
            '([Lcom/google/common/util/concurrent/ListenableFuture;)'
            'Lcom/google/common/util/concurrent/Futures$FutureCombiner;',
            True, False
        ),
        (
            '(Ljava/lang/Iterable;)'
            'Lcom/google/common/util/concurrent/Futures$FutureCombiner;',
            True, False
        )
    ])
    """
    Returns a FutureCombiner that can be used to combine futures after all input futures succeed.
    
    The returned combiner can be used to create a derived future that executes a function
    when all input futures succeed. If any input future fails or is cancelled, the derived
    future fails or is cancelled with the same cause.
    
    Overloaded methods:
    1. whenAllSucceed(futures...): Takes a varargs array of ListenableFuture instances.
    2. whenAllSucceed(futures): Takes an Iterable of ListenableFuture instances.
    
    Parameters:
        futures: The input futures to monitor for success.
        
    Returns:
        A FutureCombiner that can be used to create a derived future.
    """

    nonCancellationPropagating = JavaStaticMethod(
            '(Lcom/google/common/util/concurrent/ListenableFuture;)'
            'Lcom/google/common/util/concurrent/ListenableFuture;'
    )
    """
    Returns a future that is equivalent to the input but does not propagate cancellation.
    
    If the returned future is cancelled, the input future is not cancelled. This is useful
    when you want to create a dependent future that can be cancelled without affecting the
    original future.
    
    Parameters:
        future: The input ListenableFuture.
        
    Returns:
        A ListenableFuture that does not propagate cancellation to the input future.
    """

    successfulAsList = JavaMultipleMethod([
        (
            '([Lcom/google/common/util/concurrent/ListenableFuture;)'
            'Lcom/google/common/util/concurrent/ListenableFuture;',
            True, False
        ),
        (
            '(Ljava/lang/Iterable;)'
            'Lcom/google/common/util/concurrent/ListenableFuture;',
            True, False
        )
    ])
    """
    Returns a ListenableFuture that succeeds when all input futures complete.
    
    The returned future succeeds with a list of the results of all input futures that succeeded.
    For input futures that failed or were cancelled, the corresponding element in the result
    list is null. Unlike allAsList(), this method always succeeds, even if some input futures fail.
    
    Overloaded methods:
    1. successfulAsList(futures...): Takes a varargs array of ListenableFuture instances.
    2. successfulAsList(futures): Takes an Iterable of ListenableFuture instances.
    
    Parameters:
        futures: The input futures to combine.
        
    Returns:
        A ListenableFuture containing a list of the results of all input futures that succeeded,
        with nulls for futures that failed or were cancelled.
    """

    inCompletionOrder = JavaStaticMethod(
        '(Ljava/lang/Iterable;)'
        'Lcom/google/common/collect/ImmutableList;'
    )
    """
    Returns an immutable list of futures that complete in the order they complete.
    
    The returned list contains the same futures as the input, but in the order they complete.
    This is useful when you want to process futures as they complete, rather than waiting
    for all of them to complete.
    
    Parameters:
        futures: The input futures to track.
        
    Returns:
        An ImmutableList of ListenableFuture instances that will complete in the order
        they complete, rather than the order they were provided.
    """

    addCallback = JavaStaticMethod(
        '(Lcom/google/common/util/concurrent/ListenableFuture;'
        'Lcom/google/common/util/concurrent/FutureCallback;'
        'Ljava/util/concurrent/Executor;)V'
    )
    """
    Adds a callback to be run when the future completes.
    
    The callback will be executed on the provided executor when the future completes.
    If the future has already completed, the callback will be executed immediately.
    
    Parameters:
        future: The ListenableFuture to add the callback to.
        callback: The FutureCallback to execute when the future completes.
        executor: The executor to run the callback on.
    """

    getDone = JavaStaticMethod(
        '(Ljava/util/concurrent/Future;)'
        'Ljava/lang/Object;'
     )
    """
    Gets the result of a Future, assuming that it is already done.
    
    This method does not block, and will throw an IllegalStateException if the future
    is not done. It's useful when you know the future is already complete.
    
    Parameters:
        future: The Future to get the result from.
        
    Returns:
        The result of the future.
        
    Throws:
        ExecutionException: If the future failed with an exception.
        IllegalStateException: If the future is not done.
    """

    getChecked = JavaMultipleMethod([
        (
            '(Ljava/util/concurrent/Future;'
            'Ljava/lang/Class;)Ljava/lang/Object;',
            True, False
        ),
        (
            '(Ljava/util/concurrent/Future;'
            'Ljava/lang/Class;JLjava/util/concurrent/TimeUnit;)'
            'Ljava/lang/Object;',
            True, False
        )
    ])
    """
    Gets the result of a Future, converting checked exceptions to a specified exception type.
    
    This method blocks until the future completes. If the future fails with a checked exception,
    it will be wrapped in an exception of the specified type.
    
    Overloaded methods:
    1. getChecked(future, exceptionClass): Waits indefinitely for the future to complete.
    2. getChecked(future, exceptionClass, timeout, unit): Waits for the specified timeout.
    
    Parameters:
        future: The Future to get the result from.
        exceptionClass: The class of exception to throw if the future fails.
        timeout: The maximum time to wait.
        unit: The time unit of the timeout parameter.
        
    Returns:
        The result of the future.
        
    Throws:
        An exception of the specified type if the future fails.
        TimeoutException: If the timeout is reached.
    """

    getUnchecked = JavaStaticMethod(
        '(Ljava/util/concurrent/Future;)'
        'Ljava/lang/Object;'
    )
    """
    Gets the result of a Future, converting checked exceptions to unchecked exceptions.
    
    This method blocks until the future completes. If the future fails with a checked exception,
    it will be wrapped in an UncheckedExecutionException.
    
    Parameters:
        future: The Future to get the result from.
        
    Returns:
        The result of the future.
        
    Throws:
        UncheckedExecutionException: If the future fails with a checked exception.
        UncheckedTimeoutException: If the future times out.
        CancellationException: If the future was cancelled.
    """
