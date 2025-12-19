## basic.py

import time
import random
import math


def wait_human(min_ms: int, max_ms: int = None):
    """Human-like pause with natural variance."""
    if max_ms is None:
        max_ms = min_ms * 1.3
    duration = random.triangular(min_ms, max_ms, (min_ms + max_ms) / 2)
    time.sleep(duration / 1000)


def _bezier_curve(p0, p1, p2, t):
    """Quadratic Bezier interpolation."""
    return (
        (1 - t) ** 2 * p0
        + 2 * (1 - t) * t * p1
        + t ** 2 * p2
    )


def move_to_target(mouse, target_x, target_y, *, current_x, current_y):
    """
    Move mouse smoothly and densely to a coordinate using a curved Bezier path.
    Returns (new_x, new_y).
    """

    dx = target_x - current_x
    dy = target_y - current_y
    distance = math.hypot(dx, dy)

    # More distance -> more points (much smoother)
    steps = max(35, int(distance / 8))

    # Random curvature for more human-like movement
    curve_strength = distance * random.uniform(0.15, 0.28)
    ctrl_x = current_x + dx * 0.5 + random.uniform(-curve_strength, curve_strength)
    ctrl_y = current_y + dy * 0.5 + random.uniform(-curve_strength, curve_strength)

    for i in range(1, steps + 1):
        t = i / steps

        # Bezier curve interpolation
        nx = _bezier_curve(current_x, ctrl_x, target_x, t)
        ny = _bezier_curve(current_y, ctrl_y, target_y, t)

        # Very small jitter for realism
        nx += random.uniform(-0.3, 0.3)
        ny += random.uniform(-0.3, 0.3)

        mouse.move(nx, ny)

        # Human reaction time for micro movement
        wait_human(18, 45)

    return target_x, target_y


def move_to_box(mouse, box, *, current_x, current_y):
    """
    Move mouse to the center of a bounding box with a small random offset.
    Returns (new_x, new_y).
    """
    cx = box["x"] + box["width"] * 0.5 + random.uniform(-4, 4)
    cy = box["y"] + box["height"] * 0.5 + random.uniform(-4, 4)
    return move_to_target(mouse, cx, cy, current_x=current_x, current_y=current_y)


def scroll_human(page, delta_y):
    """
    Human-like scroll behavior with multiple small wheel movements.
    """
    step_count = random.randint(5, 12)
    per_step = delta_y / step_count

    for _ in range(step_count):
        page.mouse.wheel(0, per_step + random.uniform(-4, 4))
        wait_human(40, 110)


def bring_into_view(page, box, viewport):
    """
    Scroll element into view with realistic timing.
    """
    top_visible = box["y"] >= 0
    bottom_visible = box["y"] + box["height"] <= viewport["height"]

    if not (top_visible and bottom_visible):
        target_scroll = box["y"] - viewport["height"] * 0.35
        page.evaluate(f"window.scrollTo(0, {int(target_scroll)})")
        wait_human(260, 650)


def idle_human(mouse, page, *, current_x, current_y):
    """
    Small idle micro-movements during browsing pauses.
    Returns updated (x, y).
    """
    if random.random() < 0.45:
        nx = current_x + random.uniform(-6, 6)
        ny = current_y + random.uniform(-4, 4)
        mouse.move(nx, ny)
        wait_human(40, 90)
        return nx, ny

    # Occasionally scroll slightly during idle
    if random.random() < 0.15:
        page.mouse.wheel(0, random.uniform(-25, 25))
        wait_human(150, 350)

    return current_x, current_y
