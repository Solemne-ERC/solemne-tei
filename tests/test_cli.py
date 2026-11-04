# SPDX-License-Identifier: MIT
import pytest

import solemne_tei
from solemne_tei import cli


def test_the_command_line_shows_its_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--version"])
    assert solemne_tei.__version__ in capsys.readouterr().out
