"""AndroidGestureControl 手勢操作規格測試 (Stage 3 - RED)。"""

from unittest.mock import MagicMock

import pytest
from appium.webdriver.common.appiumby import AppiumBy

from libraries.mobile_testing.android.AndroidGestureControl import AndroidGestureControl


@pytest.fixture
def driver():
    mock = MagicMock()
    mock.get_window_size.return_value = {'width': 1080, 'height': 1920}
    return mock


@pytest.fixture
def gestures(driver):
    return AndroidGestureControl(driver)


def _mock_element(element_id: str = 'element-id'):
    element = MagicMock()
    element.id = element_id
    return element


def test_long_press_element_finds_locator_and_calls_mobile_command(gestures, driver):
    element = _mock_element('mock-element-id')
    driver.find_element.return_value = element

    gestures.long_press_element('id=submit-button', duration=1500)

    driver.find_element.assert_called_once_with(AppiumBy.ID, 'submit-button')
    driver.execute_script.assert_called_once_with(
        'mobile: longClickGesture',
        {'elementId': 'mock-element-id', 'duration': 1500},
    )


def test_long_press_coordinates_uses_mobile_long_click(gestures, driver):
    gestures.long_press_coordinates(120, 360, duration=800)

    driver.execute_script.assert_called_once_with(
        'mobile: longClickGesture',
        {'x': 120, 'y': 360, 'duration': 800},
    )


@pytest.mark.parametrize('direction', ['up', 'down', 'left', 'right'])
def test_swipe_direction_uses_window_dimensions(gestures, driver, direction):
    driver.get_window_size.return_value = {'width': 1080, 'height': 1920}

    gestures.swipe_direction(direction=direction, percent=60)

    driver.execute_script.assert_called_once_with(
        'mobile: swipeGesture',
        {
            'left': 0,
            'top': 0,
            'width': 1080,
            'height': 1920,
            'direction': direction,
            'percent': 0.6,
        },
    )


def test_swipe_in_area_accepts_boundaries_and_direction(gestures, driver):
    gestures.swipe_in_area(
        left=10,
        top=20,
        width=200,
        height=400,
        direction='up',
        percent=80,
    )

    driver.execute_script.assert_called_once_with(
        'mobile: swipeGesture',
        {
            'left': 10,
            'top': 20,
            'width': 200,
            'height': 400,
            'direction': 'up',
            'percent': 0.8,
        },
    )


def test_tap_coordinates_uses_mobile_click_gesture(gestures, driver):
    gestures.tap_coordinates(512, 640)

    driver.execute_script.assert_called_once_with(
        'mobile: clickGesture',
        {'x': 512, 'y': 640},
    )


def test_double_tap_element_uses_mobile_double_click(gestures, driver):
    element = _mock_element('element-abc-id')
    driver.find_element.return_value = element

    gestures.double_tap_element('id=favorite')

    driver.find_element.assert_called_once_with(AppiumBy.ID, 'favorite')
    driver.execute_script.assert_called_once_with(
        'mobile: doubleClickGesture',
        {'elementId': 'element-abc-id'},
    )


def test_drag_element_uses_mobile_drag_gesture_with_speed(gestures, driver):
    element = _mock_element('drag-element-id')
    driver.find_element.return_value = element

    gestures.drag_element('id=card', end_x=200, end_y=400, speed=1500)

    driver.find_element.assert_called_once_with(AppiumBy.ID, 'card')
    driver.execute_script.assert_called_once_with(
        'mobile: dragGesture',
        {'elementId': 'drag-element-id', 'endX': 200, 'endY': 400, 'speed': 1500},
    )
