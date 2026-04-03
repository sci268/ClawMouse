import argparse
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from Util.MCPController import KeymouseGoController


mcp = FastMCP('ClawMouse MCP')
controller = KeymouseGoController()


@mcp.tool
def get_status() -> Dict[str, Any]:
    return controller.status()


@mcp.tool
def list_scripts() -> Dict[str, Any]:
    return {
        'scripts': controller.list_scripts(),
    }


@mcp.tool
def validate_script(script_path: str) -> Dict[str, Any]:
    return controller.validate_script(script_path)


@mcp.tool
def run_script(script_path: str, runtimes: int = 1) -> Dict[str, Any]:
    return controller.run_script(script_path, runtimes)


@mcp.tool
def start_script(script_path: str, runtimes: int = 1) -> Dict[str, Any]:
    return controller.start_script(script_path, runtimes)


@mcp.tool
def stop_execution() -> Dict[str, Any]:
    return controller.stop()


@mcp.tool
def mouse_move(x: int, y: int, delay: int = 0) -> Dict[str, Any]:
    return controller.mouse_move(x, y, delay)


@mcp.tool
def mouse_click(
    button: str = 'left',
    x: Optional[int] = None,
    y: Optional[int] = None,
    times: int = 1,
    hold_ms: int = 50,
    delay: int = 0,
) -> Dict[str, Any]:
    return controller.mouse_click(button, x, y, times, hold_ms, delay)


@mcp.tool
def mouse_scroll(direction: str = 'up', times: int = 1, delay: int = 0) -> Dict[str, Any]:
    return controller.mouse_scroll(direction, times, delay)


@mcp.tool
def key_down(
    key: str,
    key_code: Optional[int] = None,
    extended: Optional[bool] = None,
    delay: int = 0,
) -> Dict[str, Any]:
    return controller.key_down(key, key_code, extended, delay)


@mcp.tool
def key_up(
    key: str,
    key_code: Optional[int] = None,
    extended: Optional[bool] = None,
    delay: int = 0,
) -> Dict[str, Any]:
    return controller.key_up(key, key_code, extended, delay)


@mcp.tool
def key_tap(
    key: str,
    key_code: Optional[int] = None,
    extended: Optional[bool] = None,
    times: int = 1,
    hold_ms: int = 50,
    delay: int = 0,
) -> Dict[str, Any]:
    return controller.key_tap(key, key_code, extended, times, hold_ms, delay)


@mcp.tool
def hotkey(keys: list[str], hold_ms: int = 50, delay: int = 0) -> Dict[str, Any]:
    return controller.hotkey(keys, hold_ms, delay)


@mcp.tool
def wait_ms(ms: int) -> Dict[str, Any]:
    return controller.wait_ms(ms)


@mcp.tool
def wait_until_idle(timeout_ms: int = 0, poll_ms: int = 100) -> Dict[str, Any]:
    return controller.wait_until_idle(timeout_ms, poll_ms)


@mcp.tool
def text_input(text: str, delay: int = 0) -> Dict[str, Any]:
    return controller.text_input(text, delay)


@mcp.tool
def type_and_enter(text: str, delay: int = 0, hold_ms: int = 50) -> Dict[str, Any]:
    return controller.type_and_enter(text, delay, hold_ms)


@mcp.tool
def double_click(
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = 'left',
    hold_ms: int = 50,
    delay: int = 0,
) -> Dict[str, Any]:
    return controller.double_click(x, y, button, hold_ms, delay)


@mcp.tool
def drag(
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
    button: str = 'left',
    hold_ms: int = 50,
    move_delay: int = 0,
    release_delay: int = 0,
) -> Dict[str, Any]:
    return controller.drag(from_x, from_y, to_x, to_y, button, hold_ms, move_delay, release_delay)


@mcp.tool
def get_cursor_pos() -> Dict[str, Any]:
    return controller.get_cursor_pos()


@mcp.tool
def get_foreground_window() -> Dict[str, Any]:
    return controller.get_foreground_window()


@mcp.tool
def list_windows(title_filter: str = '', visible_only: bool = True, limit: int = 50) -> Dict[str, Any]:
    return controller.list_windows(title_filter, visible_only, limit)


@mcp.tool
def find_window(
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    limit: int = 20,
) -> Dict[str, Any]:
    return controller.find_window(title_substring, exact_title, class_name, visible_only, limit)


@mcp.tool
def focus_window(hwnd: int, restore: bool = True) -> Dict[str, Any]:
    return controller.focus_window(hwnd, restore)


@mcp.tool
def move_window(
    x: int,
    y: int,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    restore: bool = True,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.move_window(x, y, hwnd, title_substring, exact_title, class_name, visible_only, restore, width, height)


@mcp.tool
def drag_window(
    to_x: int,
    to_y: int,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    restore: bool = True,
) -> Dict[str, Any]:
    return controller.drag_window(to_x, to_y, hwnd, title_substring, exact_title, class_name, visible_only, restore)


@mcp.tool
def focus_window_by_title(
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    restore: bool = True,
) -> Dict[str, Any]:
    return controller.focus_window_by_title(title_substring, exact_title, class_name, visible_only, restore)


@mcp.tool
def set_window_guard(
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    focus: bool = False,
    restore: bool = True,
) -> Dict[str, Any]:
    return controller.set_window_guard(hwnd, title_substring, exact_title, class_name, visible_only, focus, restore)


@mcp.tool
def get_window_guard() -> Dict[str, Any]:
    return controller.get_window_guard()


@mcp.tool
def clear_window_guard() -> Dict[str, Any]:
    return controller.clear_window_guard()


@mcp.tool
def capture_window(
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    focus: bool = False,
    restore: bool = True,
    wait_after_focus_ms: int = 150,
    prefix: str = 'window',
) -> Dict[str, Any]:
    return controller.capture_window(
        hwnd,
        title_substring,
        exact_title,
        class_name,
        visible_only,
        focus,
        restore,
        wait_after_focus_ms,
        prefix,
    )


@mcp.tool
def capture_window_region(
    offset_x: int,
    offset_y: int,
    width: int,
    height: int,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    focus: bool = False,
    restore: bool = True,
    wait_after_focus_ms: int = 150,
    prefix: str = 'window_region',
) -> Dict[str, Any]:
    return controller.capture_window_region(
        offset_x,
        offset_y,
        width,
        height,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        visible_only,
        focus,
        restore,
        wait_after_focus_ms,
        prefix,
    )


@mcp.tool
def capture_window_partition_map(
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    rows: int = 2,
    cols: int = 2,
    visible_only: bool = True,
    focus: bool = False,
    restore: bool = True,
    wait_after_focus_ms: int = 150,
    prefix: str = 'window_partition',
) -> Dict[str, Any]:
    return controller.capture_window_partition_map(
        hwnd,
        title_substring,
        exact_title,
        class_name,
        rows,
        cols,
        visible_only,
        focus,
        restore,
        wait_after_focus_ms,
        prefix,
    )


@mcp.tool
def list_screenshot_profiles() -> Dict[str, Any]:
    return controller.list_screenshot_profiles()


@mcp.tool
def get_bridge_status(base_dir: Optional[str] = None) -> Dict[str, Any]:
    return controller.get_bridge_status(base_dir)


@mcp.tool
def trae_status(
    base_dir: Optional[str] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    sample_limit: int = 3,
) -> Dict[str, Any]:
    return controller.trae_status(base_dir, title_substring, exact_title, class_name, visible_only, sample_limit)


@mcp.tool
def send_bridge_task(
    task_type: str,
    content: str,
    task_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    expectation: Optional[Dict[str, Any]] = None,
    from_agent: str = 'LobsterAI',
    to_agent: str = 'Trae',
    base_dir: Optional[str] = None,
) -> Dict[str, Any]:
    return controller.send_bridge_task(task_type, content, task_id, context, expectation, from_agent, to_agent, base_dir)


@mcp.tool
def list_bridge_tasks(status: Optional[str] = None, base_dir: Optional[str] = None) -> Dict[str, Any]:
    return controller.list_bridge_tasks(status, base_dir)


@mcp.tool
def list_bridge_replies(status: Optional[str] = None, base_dir: Optional[str] = None) -> Dict[str, Any]:
    return controller.list_bridge_replies(status, base_dir)


@mcp.tool
def read_bridge_reply(task_id: str, archive_on_read: bool = False, base_dir: Optional[str] = None) -> Dict[str, Any]:
    return controller.read_bridge_reply(task_id, archive_on_read, base_dir)


@mcp.tool
def wait_bridge_reply(
    task_id: str,
    timeout_s: int = 60,
    initial_poll_ms: int = 200,
    max_poll_ms: int = 2000,
    archive_on_read: bool = False,
    base_dir: Optional[str] = None,
) -> Dict[str, Any]:
    return controller.wait_bridge_reply(task_id, timeout_s, initial_poll_ms, max_poll_ms, archive_on_read, base_dir)


@mcp.tool
def write_bridge_reply(
    task_id: str,
    result: Any,
    status: str = 'success',
    from_agent: str = 'Trae',
    to_agent: str = 'LobsterAI',
    error: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> Dict[str, Any]:
    return controller.write_bridge_reply(task_id, result, status, from_agent, to_agent, error, base_dir)


@mcp.tool
def claim_bridge_task(task_id: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    return controller.claim_bridge_task(task_id, base_dir)


@mcp.tool
def archive_bridge_task(task_id: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    return controller.archive_bridge_task(task_id, base_dir)


@mcp.tool
def get_screenshot_profile(profile_name: str) -> Dict[str, Any]:
    return controller.get_screenshot_profile(profile_name)


@mcp.tool
def reset_screenshot_profile(profile_name: str) -> Dict[str, Any]:
    return controller.reset_screenshot_profile(profile_name)


@mcp.tool
def save_screenshot_profile_partitions(profile_name: str, partitions: list[dict]) -> Dict[str, Any]:
    return controller.save_screenshot_profile_partitions(profile_name, partitions)


@mcp.tool
def prepare_layout_analysis(
    profile_name: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    wait_after_focus_ms: Optional[int] = None,
    prefix: Optional[str] = None,
    include_inline_image: bool = True,
    preview_max_width: int = 1280,
) -> Dict[str, Any]:
    return controller.prepare_layout_analysis(
        profile_name,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        visible_only,
        focus,
        restore,
        wait_after_focus_ms,
        prefix,
        include_inline_image,
        preview_max_width,
    )


@mcp.tool
def capture_profile_window(
    profile_name: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    wait_after_focus_ms: Optional[int] = None,
    prefix: Optional[str] = None,
) -> Dict[str, Any]:
    return controller.capture_profile_window(
        profile_name,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        visible_only,
        focus,
        restore,
        wait_after_focus_ms,
        prefix,
    )


@mcp.tool
def capture_profile_region(
    profile_name: str,
    offset_x: int,
    offset_y: int,
    width: int,
    height: int,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    wait_after_focus_ms: Optional[int] = None,
    prefix: Optional[str] = None,
) -> Dict[str, Any]:
    return controller.capture_profile_region(
        profile_name,
        offset_x,
        offset_y,
        width,
        height,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        visible_only,
        focus,
        restore,
        wait_after_focus_ms,
        prefix,
    )


@mcp.tool
def capture_profile_partition_map(
    profile_name: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    wait_after_focus_ms: Optional[int] = None,
    prefix: Optional[str] = None,
) -> Dict[str, Any]:
    return controller.capture_profile_partition_map(
        profile_name,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        rows,
        cols,
        visible_only,
        focus,
        restore,
        wait_after_focus_ms,
        prefix,
    )


@mcp.tool
def click_window_center(
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    button: str = 'left',
    double: bool = False,
    visible_only: bool = True,
    focus: bool = False,
    restore: bool = True,
    hold_ms: int = 50,
    delay: int = 0,
) -> Dict[str, Any]:
    return controller.click_window_center(
        hwnd,
        title_substring,
        exact_title,
        class_name,
        button,
        double,
        visible_only,
        focus,
        restore,
        hold_ms,
        delay,
    )


@mcp.tool
def click_in_window(
    offset_x: int,
    offset_y: int,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    button: str = 'left',
    double: bool = False,
    visible_only: bool = True,
    focus: bool = False,
    restore: bool = True,
    hold_ms: int = 50,
    delay: int = 0,
) -> Dict[str, Any]:
    return controller.click_in_window(
        offset_x,
        offset_y,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        button,
        double,
        visible_only,
        focus,
        restore,
        hold_ms,
        delay,
    )


@mcp.tool
def drag_in_window(
    from_offset_x: int,
    from_offset_y: int,
    to_offset_x: int,
    to_offset_y: int,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    button: str = 'left',
    visible_only: bool = True,
    focus: bool = False,
    restore: bool = True,
    hold_ms: int = 50,
    move_delay: int = 0,
    release_delay: int = 0,
) -> Dict[str, Any]:
    return controller.drag_in_window(
        from_offset_x,
        from_offset_y,
        to_offset_x,
        to_offset_y,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        button,
        visible_only,
        focus,
        restore,
        hold_ms,
        move_delay,
        release_delay,
    )


@mcp.tool
def send_message_to_window(
    text: str,
    input_offset_x: int,
    input_offset_y: int,
    send_button_offset_x: Optional[int] = None,
    send_button_offset_y: Optional[int] = None,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    submit_mode: str = 'click',
    visible_only: bool = True,
    focus: bool = True,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: int = 0,
    enter_times: int = 1,
    click_before_enter: bool = False,
    click_before_enter_delay_ms: int = 120,
) -> Dict[str, Any]:
    return controller.send_message_to_window(
        text,
        input_offset_x,
        input_offset_y,
        send_button_offset_x,
        send_button_offset_y,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def build_trae_bridge_prompt(
    task_id: str,
    content: str,
    expected_reply: Optional[str] = None,
) -> Dict[str, Any]:
    return controller.build_trae_bridge_prompt(task_id, content, expected_reply)


@mcp.tool
def trae_send_bridge_message(
    task_id: str,
    content: str,
    expected_reply: Optional[str] = None,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    submit_mode: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
    click_before_enter: Optional[bool] = None,
    click_before_enter_delay_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.trae_send_bridge_message(
        task_id,
        content,
        expected_reply,
        hwnd,
        title_substring,
        exact_title,
        input_offset_x,
        input_offset_y,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def trae_delegate(
    content: str,
    task_id: Optional[str] = None,
    expected_reply: Optional[str] = None,
    mode: str = 'bridge_task',
    context: Optional[Dict[str, Any]] = None,
    expectation: Optional[Dict[str, Any]] = None,
    from_agent: str = 'LobsterAI',
    to_agent: str = 'Trae',
    base_dir: Optional[str] = None,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    submit_mode: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
    click_before_enter: Optional[bool] = None,
    click_before_enter_delay_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.trae_delegate(
        content,
        task_id,
        expected_reply,
        mode,
        context,
        expectation,
        from_agent,
        to_agent,
        base_dir,
        hwnd,
        title_substring,
        exact_title,
        input_offset_x,
        input_offset_y,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def list_chat_profiles() -> Dict[str, Any]:
    return controller.list_chat_profiles()


@mcp.tool
def get_chat_profile(profile_name: str) -> Dict[str, Any]:
    return controller.get_chat_profile(profile_name)


@mcp.tool
def save_chat_profile(
    profile_name: str,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    submit_mode: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    send_button_offset_x: Optional[int] = None,
    send_button_offset_y: Optional[int] = None,
    input_ratio_x: Optional[float] = None,
    input_ratio_y: Optional[float] = None,
    send_ratio_x: Optional[float] = None,
    send_ratio_y: Optional[float] = None,
    focus: Optional[bool] = None,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
    click_before_enter: Optional[bool] = None,
    click_before_enter_delay_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.save_chat_profile(
        profile_name,
        title_substring,
        exact_title,
        class_name,
        submit_mode,
        input_offset_x,
        input_offset_y,
        send_button_offset_x,
        send_button_offset_y,
        input_ratio_x,
        input_ratio_y,
        send_ratio_x,
        send_ratio_y,
        focus,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def reset_chat_profile(profile_name: str) -> Dict[str, Any]:
    return controller.reset_chat_profile(profile_name)


@mcp.tool
def inspect_cursor_in_window(
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
) -> Dict[str, Any]:
    return controller.inspect_cursor_in_window(hwnd, title_substring, exact_title, class_name, visible_only)


@mcp.tool
def calibrate_chat_profile_point(
    profile_name: str,
    point_name: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    visible_only: bool = True,
    use_ratio: bool = True,
) -> Dict[str, Any]:
    return controller.calibrate_chat_profile_point(
        profile_name,
        point_name,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        visible_only,
        use_ratio,
    )


@mcp.tool
def send_message_with_profile(
    profile_name: str,
    text: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    class_name: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    send_button_offset_x: Optional[int] = None,
    send_button_offset_y: Optional[int] = None,
    submit_mode: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
    click_before_enter: Optional[bool] = None,
    click_before_enter_delay_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.send_message_with_profile(
        profile_name,
        text,
        hwnd,
        title_substring,
        exact_title,
        class_name,
        input_offset_x,
        input_offset_y,
        send_button_offset_x,
        send_button_offset_y,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def browser_chat_send_message(
    text: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    submit_mode: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
    click_before_enter: Optional[bool] = None,
    click_before_enter_delay_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.browser_chat_send_message(
        text,
        hwnd,
        title_substring,
        exact_title,
        input_offset_x,
        input_offset_y,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def trae_send_message(
    text: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    submit_mode: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
    click_before_enter: Optional[bool] = None,
    click_before_enter_delay_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.trae_send_message(
        text,
        hwnd,
        title_substring,
        exact_title,
        input_offset_x,
        input_offset_y,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def wechat_send_message(
    text: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    submit_mode: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
    click_before_enter: Optional[bool] = None,
    click_before_enter_delay_ms: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.wechat_send_message(
        text,
        hwnd,
        title_substring,
        exact_title,
        input_offset_x,
        input_offset_y,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
        click_before_enter,
        click_before_enter_delay_ms,
    )


@mcp.tool
def qq_send_message(
    text: str,
    hwnd: Optional[int] = None,
    title_substring: Optional[str] = None,
    exact_title: Optional[str] = None,
    input_offset_x: Optional[int] = None,
    input_offset_y: Optional[int] = None,
    submit_mode: Optional[str] = None,
    visible_only: bool = True,
    focus: Optional[bool] = None,
    restore: bool = True,
    hold_ms: int = 50,
    input_ready_delay_ms: int = 100,
    click_delay_ms: int = 0,
    enter_delay_ms: Optional[int] = None,
    enter_times: Optional[int] = None,
) -> Dict[str, Any]:
    return controller.qq_send_message(
        text,
        hwnd,
        title_substring,
        exact_title,
        input_offset_x,
        input_offset_y,
        submit_mode,
        visible_only,
        focus,
        restore,
        hold_ms,
        input_ready_delay_ms,
        click_delay_ms,
        enter_delay_ms,
        enter_times,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--transport', default='stdio', choices=['stdio', 'http'])
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if args.transport == 'http':
        mcp.run(transport='http', host=args.host, port=args.port)
        return
    mcp.run(transport='stdio')


if __name__ == '__main__':
    main()
