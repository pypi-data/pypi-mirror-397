from __future__ import annotations

from pulka.tui.modal_manager import ModalManager


def test_modal_dimensions_respect_terminal_size_and_chrome() -> None:
    width, height = ModalManager.calculate_dimensions_for_size(
        target_width=120,
        target_height=40,
        columns=100,
        rows=20,
        chrome_height=8,
    )
    assert width == 80  # 80% of 100
    assert height >= 11  # 3 + chrome height
    assert height <= 20


def test_modal_dimensions_use_target_when_terminal_large_enough() -> None:
    width, height = ModalManager.calculate_dimensions_for_size(
        target_width=90,
        target_height=20,
        columns=200,
        rows=60,
        chrome_height=8,
    )
    assert width == 90
    assert height == 20
