"""."""

from kinematic_tracker.association.metric_giou_aligned import MetricGIoUAligned


def test_init(driver: MetricGIoUAligned) -> None:
    assert driver.aux_r.shape == (100,)
