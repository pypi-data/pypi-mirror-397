# async_basic.py

import random
import math
import asyncio


async def wait_human(min_ms: int, max_ms: int = None):
    """Human-like pause with natural variance (async)."""
    if max_ms is None:
        max_ms = min_ms * 1.3
    duration = random.triangular(min_ms, max_ms, (min_ms + max_ms) / 2)
    await asyncio.sleep(duration / 1000)


def _bezier_curve(p0, p1, p2, t):
    """Quadratic Bezier interpolation (same as sync)."""
    return (
        (1 - t) ** 2 * p0
        + 2 * (1 - t) * t * p1
        + t ** 2 * p2
    )


async def move_to_target(mouse, target_x, target_y, *, current_x, current_y):
    """
    Move mouse smoothly and densely to a coordinate using a curved Bezier path.
    Returns (new_x, new_y).
    """

    dx = target_x - current_x
    dy = target_y - current_y
    distance = math.hypot(dx, dy)

    steps = max(35, int(distance / 8))

    curve_strength = distance * random.uniform(0.15, 0.28)
    ctrl_x = current_x + dx * 0.5 + random.uniform(-curve_strength, curve_strength)
    ctrl_y = current_y + dy * 0.5 + random.uniform(-curve_strength, curve_strength)

    for i in range(1, steps + 1):
        t = i / steps

        nx = _bezier_curve(current_x, ctrl_x, target_x, t)
        ny = _bezier_curve(current_y, ctrl_y, target_y, t)

        nx += random.uniform(-0.3, 0.3)
        ny += random.uniform(-0.3, 0.3)

        await mouse.move(nx, ny)
        await wait_human(18, 45)

    return target_x, target_y


async def move_to_box(mouse, box, *, current_x, current_y):
    """Move to center of bounding box with small random offset."""
    cx = box["x"] + box["width"] * 0.5 + random.uniform(-4, 4)
    cy = box["y"] + box["height"] * 0.5 + random.uniform(-4, 4)
    return await move_to_target(mouse, cx, cy, current_x=current_x, current_y=current_y)


async def scroll_human(page, delta_y):
    """Human-like scrolling in multiple small wheel steps."""
    step_count = random.randint(5, 12)
    per_step = delta_y / step_count

    for _ in range(step_count):
        await page.mouse.wheel(0, per_step + random.uniform(-4, 4))
        await wait_human(40, 110)


async def bring_into_view(page, box, viewport):
    """Scroll element into view with realistic timing."""
    top_visible = box["y"] >= 0
    bottom_visible = box["y"] + box["height"] <= viewport["height"]

    if not (top_visible and bottom_visible):
        target_scroll = box["y"] - viewport["height"] * 0.35
        await page.evaluate(f"window.scrollTo(0, {int(target_scroll)})")
        await wait_human(260, 650)


async def idle_human(mouse, page, *, current_x, current_y):
    """Small idle micro-movements & small scrolls."""
    if random.random() < 0.45:
        nx = current_x + random.uniform(-6, 6)
        ny = current_y + random.uniform(-4, 4)
        await mouse.move(nx, ny)
        await wait_human(40, 90)
        return nx, ny

    if random.random() < 0.15:
        await page.mouse.wheel(0, random.uniform(-25, 25))
        await wait_human(150, 350)

    return current_x, current_y
