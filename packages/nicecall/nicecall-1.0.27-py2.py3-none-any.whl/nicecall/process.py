import asyncio
import collections.abc
import io
import logging
import queue
import subprocess
import threading
import time
import typing
import pathlib


type Arg = str | pathlib.Path
type Args = typing.Sequence[Arg]
type Action = collections.abc.Callable[[str | bytes], None]
type Predicate = collections.abc.Callable[[str | bytes], bool]
type ProcessQueue = asyncio.Queue[Exception | None]


class CompletedEvent():
    pass


class Process():
    """
    Provides an easy way to call processes and handle their output.
    """
    def __init__(
            self,
            on_stdout: list[Action] | None = None,
            on_stderr: list[Action] | None = None,
            filters: list[Predicate] | None = None,
            raise_if_error: bool = False,
            binary_stdout: bool = False,
            binary_chunks_size: int | None = None):
        """
        :param on_stdout: An action to perform for every line of stdout.
        :param on_stderr: An action to perform for every line of stderr.
        :param filters: The filters to apply to the lines in order to determine
            if `on_stdout` and `on_stderr` should be called. The filters are
            cumulative.
        :param raise_if_error: If true, `subprocess.CalledProcessError` is
            thrown if the process exits with a non-zero exit code. If false,
            no exception is thrown, and it belongs to the caller to check the
            exit code.
        :param binary_stdout: True if `stdout` could contain binary data and
            should not be processed as a series of UTF-8 lines.
        :param binary_chunks_size: The maximum size of every chunk, when
            streaming binary `stdout`.
        """
        self._on_stdout = on_stdout or []
        self._on_stderr = on_stderr or []
        self._filters = filters or []
        self._raise_if_error = raise_if_error
        self._binary_stdout = binary_stdout
        self._binary_chunks_size = binary_chunks_size

    def _clone(self) -> typing.Self:
        return self.__class__(
            self._on_stdout[:],
            self._on_stderr[:],
            self._filters[:],
            self._raise_if_error,
            self._binary_stdout,
            self._binary_chunks_size)

    def execute(
            self,
            args: Args,
            log_error: bool = True) -> int:
        """
        Runs a process and returns its exit code when it finishes (or throws an
        exception if it exits with a non-zero exit code and if `raise_if_error`
        was set).
        """
        Process._check_args(args)

        log_command = self._generate_log_command(args)
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            logger.addHandler(logging.NullHandler())
        logger.info(f"Called “{log_command}”.")

        with subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
            self._process_std(process)
            process.wait()

            exitcode = process.returncode
            if exitcode and log_error:
                logger.warning(
                    f"“{log_command}” failed with exit code {exitcode}.")

            if exitcode != 0 and self._raise_if_error:
                raise subprocess.CalledProcessError(exitcode, args[0])

            return exitcode

    def read_stdout(self, args: Args) -> typing.Sequence[str]:
        """
        Runs a process, raising an exception if it fails, and capturing its
        stdout to a list of lines.

        :param args: The process itself, and the arguments to pass to it.

        :return: The lines that correspond to the stdout, without the `\n` at
        the end.
        """
        stdout = []
        self.on_stdout(stdout.append).raise_if_error().execute(args)
        return stdout

    def stream_text_stdout(
            self,
            args: Args) -> typing.Generator[str, None, None]:
        """
        Runs a process, raising an exception if it fails, and returning its
        stdout in a form of a generator where every item corresponds to a line.

        :param args: The process itself, and the arguments to pass to it.

        :return: Zero or more lines coming from stdout, exactly as they are
        sent by the process, i.e. if they end by a new line character, it will
        not be removed.
        """
        self._binary_stdout = False
        self._binary_chunks_size = None
        return self._stream_stdout(args)

    def stream_binary_stdout(
            self,
            args: Args,
            chunks_size: int = 1024) -> typing.Generator[bytes, None, None]:
        """
        Runs a process, raising an exception if it fails, and returning its
        stdout in a form of a generator.

        :param args: The process itself, and the arguments to pass to it.

        :param chunks_size: The maximum size of every chunk.

        :return: Zero or more blocks of bytes.
        """
        self._binary_stdout = True
        self._binary_chunks_size = chunks_size
        return self._stream_stdout(args)

    def _stream_stdout(
            self,
            args: Args) -> typing.Generator[str | bytes, None, None]:
        stdout_queue: queue.Queue[
            str | bytes | Exception | CompletedEvent] = queue.Queue()

        def run():
            global child_exception
            try:
                exitcode = self.on_stdout(stdout_queue.put).execute(args)
                stdout_queue.put(
                    CompletedEvent()
                    if exitcode == 0
                    else subprocess.CalledProcessError(exitcode, args[0])
                )
            except Exception as ex:
                stdout_queue.put(ex)

        thread = threading.Thread(target=run)
        thread.start()

        while True:
            line = stdout_queue.get()

            if isinstance(line, CompletedEvent):
                break

            if isinstance(line, Exception):
                raise line

            yield line

        thread.join()

    def keep(self, predicate: Predicate) -> typing.Self:
        """
        Ensures only the lines of stdout and stderr that match a predicate are
        kept for being processed by `on_stdout` and `on_stderr`.

        Note that conditions specified with `keep` and `ignore` are cumulative.

        :param predicate: The action that takes a line as a parameter and
            returns true if the line should be kept, or false otherwise.
        :return: A new instance of process with an additional filter.
        """
        result = self._clone()
        result._filters.append(predicate)
        return result

    def ignore(self, predicate: Predicate) -> typing.Self:
        """
        Ensures the lines of stdout and stderr that match a predicate are
        discarded and will not be processed by `on_stdout` and `on_stderr`.

        Note that conditions specified with `keep` and `ignore` are cumulative.

        :param predicate: The action that takes a line as a parameter and
            returns true if the line should be kept, or false otherwise.
        :return: A new instance of process with an additional filter.
        """
        return self.keep(self._invert(predicate))

    def _generate_log_command(self, args: Args) -> str:
        """
        Generates a string representation of a command for logging purposes
        only. This string is not used when calling the actual process.
        """
        def process_item(arg):
            text = str(arg)
            return (
                f'"{text.replace('"', '\\"')}"'
                if " " in text or '"' in text
                else text)

        return " ".join(map(process_item, args))

    def _process_std(
            self,
            process: subprocess.Popen[str] | subprocess.Popen[bytes]) -> None:
        """
        Processes stdout and stderr of the process (if `on_stdout` and
        `on_stderr` were set), and waits until the process terminates.
        """
        size = (1 if self._on_stdout else 0) + (1 if self._on_stderr else 0)
        if size == 0:
            return

        # The queue is necessary to ensure stdout and stderr streams are
        # processed completely before waiting for process termination. If this
        # queue is not used, what could happen is that if Python takes too much
        # time processing lines from stdout or stderr within the threads, the
        # process will end, eventually leading to Python program stopping
        # itself and terminating the threads which were still processing
        # output.
        queue: ProcessQueue = asyncio.Queue(maxsize=size)

        if self._on_stdout:
            assert process.stdout is not None
            self._read_stream_async(
                process.stdout,
                self._on_stdout,
                queue,
                self._binary_stdout,
                self._binary_chunks_size)

        if self._on_stderr:
            assert process.stderr is not None
            self._read_stream_async(
                process.stderr, self._on_stderr, queue, False, None)

        while not queue.full():
            # The queue capacity is set to the number of streams being listened
            # to, that is, from one to two (if zero, the method would exit).
            # Once the full capacity is reached, this means all streams
            # terminated.
            time.sleep(0.005)

        # The queue now contains for every thread either `None` if the thread
        # terminated successfully, or the exception if the one was raised.
        # Let's walk through the queue and raise the swallowed exceptions on
        # the main thread.
        while not queue.empty():
            result = queue.get_nowait()
            if result is not None:
                raise result

    def _invert(self, predicate: Predicate) -> Predicate:
        def result(line: str | bytes) -> bool:
            return not predicate(line)

        return result

    def on_stdout(self, action: Action) -> typing.Self:
        """
        Adds an action to perform for every line of stdout.

        :param action: The action that takes a line as a parameter.
        :return: A new instance of process with an additional action.
        """
        result = self._clone()
        result._on_stdout.append(action)
        return result

    def on_stderr(self, action: Action) -> typing.Self:
        """
        Adds an action to perform for every line of stderr.

        :param action: The action that takes a line as a parameter.
        :return: A new instance of process with an additional action.
        """
        result = self._clone()
        result._on_stderr.append(action)
        return result

    def raise_if_error(self) -> typing.Self:
        """
        Ensures `subprocess.CalledProcessError` is thrown if the process exits
        with a non-zero exit code.
        """
        result = self._clone()
        result._raise_if_error = True
        return result

    def _read_stream_async(
            self,
            stream: typing.IO[str] | typing.IO[bytes],
            actions: typing.Sequence[Action],
            queue: ProcessQueue,
            binary: bool,
            chunks_size: int | None) -> None:
        if binary:
            assert chunks_size is not None
        else:
            assert chunks_size is None

        task = threading.Thread(
            target=self._read_stream,
            args=(stream, actions, queue, binary, chunks_size))
        task.start()

    def _read_stream(
            self,
            stream: io.TextIOWrapper,
            actions: typing.Sequence[Action],
            queue: ProcessQueue,
            binary: bool,
            chunks_size: int | None) -> None:
        try:
            while True:
                chunk = (
                    stream.read(chunks_size)
                    if binary
                    else stream.readline())
                if not chunk:
                    break

                if not binary:
                    assert isinstance(chunk, bytes)
                    chunk = chunk.decode('utf8').strip('\n')

                self._process_part(chunk, actions)

            queue.put_nowait(None)
        except Exception as e:
            queue.put_nowait(e)

    def _process_part(
            self,
            part: str | bytes,
            actions: typing.Sequence[Action]) -> None:
        if all((prefilter(part) for prefilter in self._filters)):
            for action in actions:
                action(part)

    @staticmethod
    def _check_args(args: Args) -> None:
        for index, arg in enumerate(args):
            if not isinstance(arg, str) and not isinstance(arg, pathlib.Path):
                raise TypeError(
                    f"Argument {index} (value {arg}) should be either a "
                    f"string or a pathlib.Path, not {type(arg)}.")
