import nicecall
import typing


type Lines = list[str]


class ProcessStub(nicecall.Process):
    def __init__(
            self,
            on_stdout: list[nicecall.Action] | None = None,
            on_stderr: list[nicecall.Action] | None = None,
            filters: list[nicecall.Predicate] | None = None,
            raise_if_error: bool = False,
            matches: dict[str, typing.Tuple[int, Lines, Lines]] | None = None):
        self._matches = matches or {}
        super().__init__(on_stdout, on_stderr, filters, raise_if_error)

    def add_match(
            self,
            args: nicecall.Args,
            exitcode: int,
            stdout=[],
            stderr=[]) -> None:
        key = self._generate_key(args)
        self._matches[key] = (exitcode, stdout, stderr)

    def execute(
            self,
            args: nicecall.Args,
            log_error: bool = True) -> int:
        key = self._generate_key(args)
        exitcode, stdout, stderr = self._matches[key]

        for line in stdout:
            for action in self._on_stdout:
                action(line)

        for line in stderr:
            for action in self._on_stderr:
                action(line)

        return exitcode

    def _generate_key(self, args: nicecall.Args) -> str:
        parts = [
            str(arg).replace("\\", "\\\\").replace(",", "\\,")
            for arg
            in args
        ]
        return ",".join(parts)

    def _clone(self) -> typing.Self:
        return self.__class__(
            self._on_stdout,
            self._on_stderr,
            self._filters,
            self._raise_if_error,
            self._matches)
