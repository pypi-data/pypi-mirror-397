import sys

STAGES = [
    "mashing",
    "boiling",
    "fermenting",
    "conditioning",
    "cheers 🍻"
]

class BrewBar:
    def __init__(self, iterable, width=8):
        self.iterable = iterable
        self.width = width

        try:
            self.total = len(iterable)
        except TypeError:
            self.total = None

    def __iter__(self):
        if self.total == 0:
            return iter(())

        for i, item in enumerate(self.iterable, 1):
            self._render(i)
            yield item

        if self.total is not None:
            self._render(self.total)
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _render(self, current):
        if self.total is None:
            return

        percent = current / self.total
        filled = int(self.width * percent)
        empty = self.width - filled

        stage_index = min(
            int(percent * len(STAGES)),
            len(STAGES) - 1
        )
        stage = STAGES[stage_index]

        bar = "🍺" * filled + "░" * empty
        pct = int(percent * 100)

        sys.stdout.write(f"\r{bar}  {pct}%  {stage}")
        sys.stdout.flush()


def bar(iterable, width=8):
    """Wrap an iterable with a beer-brewing progress bar.

    Args:
        iterable: Any iterable to track progress on
        width: Width of the progress bar (default: 8)

    Returns:
        BrewBar instance wrapping the iterable
    """
    return BrewBar(iterable, width=width)