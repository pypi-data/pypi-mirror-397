from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Optional,
    TypeVar,
)
from builtins import range as _range

T_SOURCE = TypeVar("T_SOURCE")
T_RESULT = TypeVar("T_RESULT")

T_ZIP_INNER = TypeVar("T_ZIP_INNER")
T_ZIP_OUTER = TypeVar("T_ZIP_OUTER")
T_ZIP_RESULT = TypeVar("T_ZIP_RESULT")

T_JOIN_INNER = TypeVar("T_JOIN_INNER")
T_JOIN_SELECTOR_RESULT = TypeVar("T_JOIN_SELECTOR_RESULT")
T_JOIN_RESULT = TypeVar("T_JOIN_RESULT")


class linq(Generic[T_SOURCE]):
    def __init__(self, src: Iterator[T_SOURCE]) -> None:
        self.__src = src

    def __iter__(self) -> Iterator[T_SOURCE]:
        yield from self.__src

    def count(self, pred: Optional[Callable[[T_SOURCE], bool]] = None) -> int:
        if pred is None:
            return sum(1 for _ in self)
        else:
            return sum(1 for e in self if pred(e))

    def any(self, pred: Optional[Callable[[T_SOURCE], bool]] = None) -> bool:
        if pred is None:
            return any(self)
        else:
            return any(pred(e) for e in self)

    def where(self, pred: Callable[[T_SOURCE], bool]) -> "linq[T_SOURCE]":
        return linq(e for e in self if pred(e))

    def select(self, pred: Callable[[T_SOURCE], T_RESULT]) -> "linq[T_RESULT]":
        return linq(pred(e) for e in self)

    def zip(
        self,
        other: Iterable[T_ZIP_OUTER],
        selector: Callable[[T_SOURCE, T_ZIP_OUTER], T_ZIP_RESULT],
    ) -> "linq[T_ZIP_RESULT]":
        return linq(selector(x, y) for x, y in zip(self, other))

    def join(
        self,
        inner: Iterable[T_JOIN_INNER],
        outer_selector: Callable[[T_SOURCE], T_JOIN_SELECTOR_RESULT],
        inner_selector: Callable[[T_JOIN_INNER], T_JOIN_SELECTOR_RESULT],
        result_selector: Callable[[T_SOURCE, T_JOIN_INNER], T_JOIN_RESULT],
    ) -> "linq[T_JOIN_RESULT]":
        def generator():
            inner_table = {}
            for item in inner:
                inner_table.setdefault(inner_selector(item), []).append(item)

            for oi in self:
                ok = outer_selector(oi)
                if ok in inner_table:
                    for ii in inner_table[ok]:
                        yield result_selector(oi, ii)

        return linq(generator())

    def first(
        self, pred: Optional[Callable[[T_SOURCE], bool]] = None
    ) -> Optional[T_SOURCE]:
        for e in self:
            if pred is None or pred(e):
                return e
        return None

    def last(self, pred: Optional[Callable[[T_SOURCE], bool]] = None) -> T_SOURCE:
        if pred is None:
            try:
                return next(reversed(self.__src))  # type: ignore
            except (TypeError, StopIteration):
                pass

        last_item = None
        found = False
        for e in self:
            if pred is None or pred(e):
                last_item = e
                found = True

        if not found:
            raise ValueError()
        return last_item  # type: ignore

    def order_by(
        self,
        selector: Callable[[T_SOURCE], Any],
        descending: bool = False,
    ) -> "linq[T_SOURCE]":
        def generator():
            items = list(self)
            items.sort(key=selector, reverse=descending)
            for item in items:
                yield item

        return linq(generator())


def repeat(e: T_SOURCE, count: int) -> linq[T_SOURCE]:
    return linq(e for _ in _range(count))


def range(start: int, count: int) -> linq[int]:
    return linq(i for i in _range(start, start + count))
