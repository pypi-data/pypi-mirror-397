import re
import sys
import time
from typing import Any

from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.padding import Padding
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    Task,
    TextColumn,
    TimeRemainingColumn,
)
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from typing_extensions import Self


class ProgressLogger:
    def __init__(self, msg: str, verbose: bool = True) -> None:
        self.msg = msg
        self.verbose = verbose

        self.logs: list[str] = []

        self.start_time: float | None = None
        self.end_time: float | None = None

    @classmethod
    def default(cls, msg: str, verbose: bool = True) -> 'ProgressLogger':
        from kumoai import in_snowflake_notebook

        if in_snowflake_notebook():
            return StreamlitProgressLogger(msg, verbose)
        return RichProgressLogger(msg, verbose)

    @property
    def duration(self) -> float:
        assert self.start_time is not None
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.perf_counter() - self.start_time

    def log(self, msg: str) -> None:
        self.logs.append(msg)

    def init_progress(self, total: int, description: str) -> None:
        pass

    def step(self) -> None:
        pass

    def __enter__(self) -> Self:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_time = time.perf_counter()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.msg})'


class ColoredMofNCompleteColumn(MofNCompleteColumn):
    def __init__(self, style: str = 'green') -> None:
        super().__init__()
        self.style = style

    def render(self, task: Task) -> Text:
        return Text(str(super().render(task)), style=self.style)


class ColoredTimeRemainingColumn(TimeRemainingColumn):
    def __init__(self, style: str = 'cyan') -> None:
        super().__init__()
        self.style = style

    def render(self, task: Task) -> Text:
        return Text(str(super().render(task)), style=self.style)


class RichProgressLogger(ProgressLogger):
    def __init__(
        self,
        msg: str,
        verbose: bool = True,
        refresh_per_second: int = 10,
    ) -> None:
        super().__init__(msg=msg, verbose=verbose)

        self.refresh_per_second = refresh_per_second

        self._progress: Progress | None = None
        self._task: int | None = None

        self._live: Live | None = None
        self._exception: bool = False

    def init_progress(self, total: int, description: str) -> None:
        assert self._progress is None
        if self.verbose:
            self._progress = Progress(
                TextColumn(f'   ↳ {description}', style='dim'),
                BarColumn(bar_width=None),
                ColoredMofNCompleteColumn(style='dim'),
                TextColumn('•', style='dim'),
                ColoredTimeRemainingColumn(style='dim'),
            )
            self._task = self._progress.add_task("Progress", total=total)

    def step(self) -> None:
        if self.verbose:
            assert self._progress is not None
            assert self._task is not None
            self._progress.update(self._task, advance=1)  # type: ignore

    def __enter__(self) -> Self:
        from kumoai import in_notebook

        super().__enter__()

        if not in_notebook():  # Render progress bar in TUI.
            sys.stdout.write("\x1b]9;4;3\x07")
            sys.stdout.flush()

        if self.verbose:
            self._live = Live(
                self,
                refresh_per_second=self.refresh_per_second,
                vertical_overflow='visible',
            )
            self._live.start()

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        from kumoai import in_notebook

        super().__exit__(exc_type, exc_val, exc_tb)

        if exc_type is not None:
            self._exception = True

        if self._progress is not None:
            self._progress.stop()
            self._progress = None
            self._task = None

        if self._live is not None:
            self._live.update(self, refresh=True)
            self._live.stop()
            self._live = None

        if not in_notebook():
            sys.stdout.write("\x1b]9;4;0\x07")
            sys.stdout.flush()

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions,
    ) -> RenderResult:

        table = Table.grid(padding=(0, 1))

        icon: Text | Padding
        if self._exception:
            style = 'red'
            icon = Text('❌', style=style)
        elif self.end_time is not None:
            style = 'green'
            icon = Text('✅', style=style)
        else:
            style = 'cyan'
            icon = Padding(Spinner('dots', style=style), (0, 1, 0, 0))

        title = Text.from_markup(
            f'{self.msg} ({self.duration:.2f}s)',
            style=style,
        )
        table.add_row(icon, title)

        for log in self.logs:
            table.add_row('', Text(f'↳ {log}', style='dim'))

        yield table

        if self.verbose and self._progress is not None:
            yield self._progress.get_renderable()


class StreamlitProgressLogger(ProgressLogger):
    def __init__(
        self,
        msg: str,
        verbose: bool = True,
    ) -> None:
        super().__init__(msg=msg, verbose=verbose)

        self._status: Any = None

        self._total = 0
        self._current = 0
        self._description: str = ''
        self._progress: Any = None

    def __enter__(self) -> Self:
        super().__enter__()

        import streamlit as st

        # Adjust layout for prettier output:
        st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)

        if self.verbose:
            self._status = st.status(
                f':blue[{self._sanitize_text(self.msg)}]',
                expanded=True,
            )

        return self

    def log(self, msg: str) -> None:
        super().log(msg)
        if self.verbose and self._status is not None:
            self._status.write(self._sanitize_text(msg))

    def init_progress(self, total: int, description: str) -> None:
        if self.verbose and self._status is not None:
            self._total = total
            self._current = 0
            self._description = self._sanitize_text(description)
            percent = min(self._current / self._total, 1.0)
            self._progress = self._status.progress(
                value=percent,
                text=f'{self._description} [{self._current}/{self._total}]',
            )

    def step(self) -> None:
        self._current += 1

        if self.verbose and self._progress is not None:
            percent = min(self._current / self._total, 1.0)
            self._progress.progress(
                value=percent,
                text=f'{self._description} [{self._current}/{self._total}]',
            )

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)

        if not self.verbose or self._status is None:
            return

        label = f'{self._sanitize_text(self.msg)} ({self.duration:.2f}s)'

        if exc_type is not None:
            self._status.update(
                label=f':red[{label}]',
                state='error',
                expanded=True,
            )
        else:
            self._status.update(
                label=f':green[{label}]',
                state='complete',
                expanded=True,
            )

    @staticmethod
    def _sanitize_text(msg: str) -> str:
        return re.sub(r'\[/?bold\]', '**', msg)


STREAMLIT_CSS = """
<style>
/* Fix horizontal scrollbar */
.stExpander summary {
    width: auto;
}

/* Fix paddings/margins */
.stExpander summary {
    padding: 0.75rem 1rem 0.5rem;
}
.stExpander p {
    margin: 0px 0px 0.2rem;
}
.stExpander [data-testid="stExpanderDetails"] {
    padding-bottom: 1.45rem;
}
.stExpander .stProgress div:first-child {
    padding-bottom: 4px;
}

/* Fix expand icon position */
.stExpander summary svg {
    height: 1.5rem;
}

/* Fix summary icons */
.stExpander summary [data-testid="stExpanderIconCheck"] {
    font-size: 1.8rem;
    margin-top: -3px;
    color: rgb(21, 130, 55);
}
.stExpander summary [data-testid="stExpanderIconError"] {
    font-size: 1.8rem;
    margin-top: -3px;
    color: rgb(255, 43, 43);
}
.stExpander summary span:first-child span:first-child {
    width: 1.6rem;
}

/* Add border between title and content */
.stExpander [data-testid="stExpanderDetails"] {
    border-top: 1px solid rgba(30, 37, 47, 0.2);
    padding-top: 0.5rem;
}

/* Fix title font size */
.stExpander summary p {
    font-size: 1rem;
}

/* Gray out content */
.stExpander [data-testid="stExpanderDetails"] {
    color: rgba(30, 37, 47, 0.5);
}

/* Fix progress bar font size */
.stExpander .stProgress p {
    line-height: 1.6;
    font-size: 1rem;
    color: rgba(30, 37, 47, 0.5);
}
</style>
"""
