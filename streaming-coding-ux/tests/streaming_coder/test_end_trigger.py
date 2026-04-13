from streaming_coder.bridge import detect_trigger, TriggerMode


def test_end_trigger_chinese():
    result = detect_trigger("派 Claude 結束")
    assert result is not None
    assert result.mode == TriggerMode.SESSION_CANCEL
    assert result.agent == "claude"


def test_end_trigger_plain():
    result = detect_trigger("結束")
    assert result is None  # Too ambiguous alone — must be in active session


def test_status_trigger():
    result = detect_trigger("派 Claude 狀態")
    assert result is not None
    assert result.mode == TriggerMode.STATUS
    assert result.agent == "claude"
