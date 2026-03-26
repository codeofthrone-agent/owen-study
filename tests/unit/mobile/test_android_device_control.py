"""AndroidDeviceControl 行為規格測試 (Stage 3 - RED)。

依據 spec 驗證各方法透過 `mobile: shell` 發送正確命令與參數。
"""

from unittest.mock import MagicMock, call

import pytest

from libraries.mobile_testing.android.AndroidDeviceControl import AndroidDeviceControl


@pytest.fixture
def driver():
    mock = MagicMock()
    mock.get_window_size.return_value = {'width': 1080, 'height': 1920}
    mock.current_package = 'com.example.app'
    return mock


@pytest.fixture
def control(driver):
    return AndroidDeviceControl(driver)


def _shell_payload(command, args):
    return {
        "command": command,
        "args": args,
        "includeStderr": True,
        "timeout": AndroidDeviceControl.SHELL_TIMEOUT_MS,
    }


def test_enable_bluetooth_uses_svc_shell_command(control, driver):
    control.enable_bluetooth()

    driver.execute_script.assert_called_once_with(
        "mobile: shell",
        _shell_payload('svc', ['bluetooth', 'enable']),
    )


def test_disable_bluetooth_uses_svc_shell_command(control, driver):
    control.disable_bluetooth()

    driver.execute_script.assert_called_once_with(
        "mobile: shell",
        _shell_payload('svc', ['bluetooth', 'disable']),
    )


def test_enable_wifi_uses_svc_shell_command(control, driver):
    control.enable_wifi()

    driver.execute_script.assert_called_once_with(
        "mobile: shell",
        _shell_payload('svc', ['wifi', 'enable']),
    )


def test_disable_wifi_uses_svc_shell_command(control, driver):
    control.disable_wifi()

    driver.execute_script.assert_called_once_with(
        "mobile: shell",
        _shell_payload('svc', ['wifi', 'disable']),
    )


def test_enable_mobile_data_starts_io_appium_settings(control, driver):
    control.enable_mobile_data()

    driver.execute_script.assert_called_once_with(
        "mobile: shell",
        _shell_payload(
            'am',
            ['start', '-n', 'io.appium.settings/.Settings', '--es', 'data', 'on'],
        ),
    )


def test_disable_mobile_data_starts_io_appium_settings(control, driver):
    control.disable_mobile_data()

    driver.execute_script.assert_called_once_with(
        "mobile: shell",
        _shell_payload(
            'am',
            ['start', '-n', 'io.appium.settings/.Settings', '--es', 'data', 'off'],
        ),
    )


def test_enable_airplane_mode_sets_setting_and_broadcasts(control, driver):
    control.enable_airplane_mode()

    assert driver.execute_script.call_args_list == [
        call("mobile: shell", _shell_payload('settings', ['put', 'global', 'airplane_mode_on', '1'])),
        call(
            "mobile: shell",
            _shell_payload(
                'am',
                [
                    'broadcast',
                    '-a',
                    'android.intent.action.AIRPLANE_MODE',
                    '--ez',
                    'state',
                    'true',
                ],
            ),
        ),
    ]


def test_disable_airplane_mode_sets_setting_and_broadcasts(control, driver):
    control.disable_airplane_mode()

    assert driver.execute_script.call_args_list == [
        call("mobile: shell", _shell_payload('settings', ['put', 'global', 'airplane_mode_on', '0'])),
        call(
            "mobile: shell",
            _shell_payload(
                'am',
                [
                    'broadcast',
                    '-a',
                    'android.intent.action.AIRPLANE_MODE',
                    '--ez',
                    'state',
                    'false',
                ],
            ),
        ),
    ]


@pytest.mark.parametrize("method_name, keycode", [
    ("volume_up", 24),
    ("volume_down", 25),
    ("volume_mute", 164),
])
def test_volume_key_presses_use_expected_keycodes(control, driver, method_name, keycode):
    getattr(control, method_name)()

    driver.press_keycode.assert_called_once_with(keycode)


def test_set_media_volume_uses_media_shell_command(control, driver):
    control.set_media_volume(7)

    driver.execute_script.assert_called_once_with(
        "mobile: shell",
        _shell_payload('media', ['volume', '--stream', '3', '--set', '7']),
    )


def test_background_app_always_uses_infinite_background(control, driver):
    control.background_app(5)

    driver.background_app.assert_called_once_with(-1)


def test_activate_app_invokes_driver_activate(control, driver):
    control.activate_app("com.example.app")

    driver.activate_app.assert_called_once_with("com.example.app")


def test_dismiss_from_recents_uses_app_switch_and_swipe(control, driver):
    control.dismiss_from_recents()

    driver.press_keycode.assert_called_once_with(187)
    driver.execute_script.assert_called_once_with(
        "mobile: swipeGesture",
        {
            'left': 0,
            'top': 0,
            'width': 1080,
            'height': 1920,
            'direction': 'up',
            'percent': 0.75,
        },
    )


def test_force_stop_app_prefers_terminate_app(control, driver):
    control.force_stop_app("com.example.app")

    driver.terminate_app.assert_called_once_with("com.example.app")
