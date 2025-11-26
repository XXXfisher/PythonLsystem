# dearpygui_lsystem_editor.py
# A simple L-System visual editor using Dear PyGui
# Features:
# - Edit axiom and production rules
# - Set iterations, angle, segment length, line width
# - Real-time generation and redraw
# - Simple pan/zoom via sliders
# Requirements: pip install dearpygui

import math
import dearpygui.dearpygui as dpg

# ------------------ L-System logic ------------------

def expand_lsystem(axiom, rules, iterations):
    """Expand the L-system grammar."""
    current = axiom
    for i in range(iterations):
        nxt = []
        for ch in current:
            nxt.append(rules.get(ch, ch))
        current = "".join(nxt)
    return current


def interpret_and_get_lines(sequence, angle_deg, step_length):
    """Interpret the sequence and return a list of line segments ((x1,y1),(x2,y2)).
    Uses turtle graphics semantics:
    F: move forward and draw
    f: move forward without drawing
    +: turn right by angle
    -: turn left by angle
    [: push state
    ]: pop state
    Any other characters are ignored (but can be used as variables)
    """
    angle = math.radians(angle_deg)
    x, y = 0.0, 0.0
    dir_angle = math.radians(90)  # start pointing "up"
    stack = []
    lines = []

    for ch in sequence:
        if ch == "F":
            nx = x + math.cos(dir_angle) * step_length
            ny = y + math.sin(dir_angle) * step_length
            lines.append(((x, y), (nx, ny)))
            x, y = nx, ny
        elif ch == "f":
            x += math.cos(dir_angle) * step_length
            y += math.sin(dir_angle) * step_length
        elif ch == "+":
            dir_angle -= angle
        elif ch == "-":
            dir_angle += angle
        elif ch == "[":
            stack.append((x, y, dir_angle))
        elif ch == "]":
            if stack:
                x, y, dir_angle = stack.pop()
        # else: ignore other symbols (or extend semantics)

    return lines

# ------------------ Dear PyGui UI ------------------

# default values
DEFAULT_AXIOM = "F"
DEFAULT_RULES = "F=F[+F]F[-F]F"
DEFAULT_ITER = 4
DEFAULT_ANGLE = 25.0
DEFAULT_LENGTH = 10.0
DEFAULT_WIDTH = 1.5

# stored state in dpg values
with dpg.value_registry():
    dpg.add_value("axiom_val", default_value=DEFAULT_AXIOM)
    dpg.add_value("rules_text", default_value=DEFAULT_RULES)
    dpg.add_value("iter_val", default_value=DEFAULT_ITER)
    dpg.add_value("angle_val", default_value=DEFAULT_ANGLE)
    dpg.add_value("length_val", default_value=DEFAULT_LENGTH)
    dpg.add_value("line_width", default_value=DEFAULT_WIDTH)
    dpg.add_value("zoom_val", default_value=1.0)
    dpg.add_value("offset_x", default_value=0.0)
    dpg.add_value("offset_y", default_value=0.0)

# create context and viewport
dpg.create_context()

# drawlist size
DRAW_W, DRAW_H = 900, 700

with dpg.window(label="L-System Editor", width=1200, height=780):
    with dpg.group(horizontal=True):
        with dpg.child_window(width=340, autosize_y=True):
            dpg.add_text("Axiom")
            dpg.add_input_text(tag="axiom_input", default_value=DEFAULT_AXIOM, callback=lambda s,a,u:dpg.set_value("axiom_val", a))
            dpg.add_spacing(count=1)
            dpg.add_text("Production rules (one per line, e.g. F=F[+F]F[-F]F)")
            dpg.add_input_text(tag="rules_input", multiline=True, height=180, default_value=DEFAULT_RULES,
                                 callback=lambda s,a,u:dpg.set_value("rules_text", a))
            dpg.add_spacing(count=1)
            dpg.add_text("Iterations")
            dpg.add_slider_int(tag="iter_slider", default_value=DEFAULT_ITER, min_value=0, max_value=8,
                                 callback=lambda s,a,u:dpg.set_value("iter_val", a))
            dpg.add_spacing(count=1)
            dpg.add_text("Angle (degrees)")
            dpg.add_slider_float(tag="angle_slider", default_value=DEFAULT_ANGLE, min_value=0, max_value=180,
                                   callback=lambda s,a,u:dpg.set_value("angle_val", a))
            dpg.add_spacing(count=1)
            dpg.add_text("Segment length (px)")
            dpg.add_slider_float(tag="length_slider", default_value=DEFAULT_LENGTH, min_value=0.1, max_value=80.0,
                                   callback=lambda s,a,u:dpg.set_value("length_val", a))
            dpg.add_spacing(count=1)
            dpg.add_text("Line width")
            dpg.add_slider_float(tag="width_slider", default_value=DEFAULT_WIDTH, min_value=0.1, max_value=10.0,
                                   callback=lambda s,a,u:dpg.set_value("line_width", a))
            dpg.add_spacing(count=1)
            dpg.add_button(label="Generate & Draw", callback=lambda: dpg.set_value("_regen", True))
            dpg.add_same_line()
            dpg.add_button(label="Reset View", callback=lambda: (dpg.set_value("zoom_val", 1.0), dpg.set_value("offset_x", 0.0), dpg.set_value("offset_y", 0.0)))
            dpg.add_spacing(count=1)
            dpg.add_text("View controls")
            dpg.add_slider_float(tag="zoom_slider", label="Zoom", default_value=1.0, min_value=0.1, max_value=10.0,
                                   callback=lambda s,a,u:dpg.set_value("zoom_val", a))
            dpg.add_slider_float(tag="pan_x", label="Pan X", default_value=0.0, min_value=-1000.0, max_value=1000.0,
                                   callback=lambda s,a,u:dpg.set_value("offset_x", a))
            dpg.add_slider_float(tag="pan_y", label="Pan Y", default_value=0.0, min_value=-1000.0, max_value=1000.0,
                                   callback=lambda s,a,u:dpg.set_value("offset_y", a))
            dpg.add_spacing(count=1)
            dpg.add_text("Tips: Use '+' and '-' in rules to turn. '[' and ']' push/pop state.")

        # drawing area
        with dpg.child_window(width=DRAW_W, height=DRAW_H):
            dpg.add_text("Canvas")
            drawlist_tag = "lsys_drawlist"
            dpg.add_drawlist(tag=drawlist_tag, width=DRAW_W, height=DRAW_H, background=[30,30,30,255])

# a hidden value to signal regen (simple approach)
with dpg.group():
    dpg.add_value(tag="_regen", default_value=False)

# ------------------ helpers ------------------

def parse_rules(text):
    rules = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            left, right = line.split("=", 1)
            left = left.strip()
            right = right.strip()
            if left:
                rules[left] = right
    return rules


def compute_and_draw():
    # read values
    axiom = dpg.get_value("axiom_input")
    rules_text = dpg.get_value("rules_input")
    iters = dpg.get_value("iter_slider")
    angle = dpg.get_value("angle_slider")
    length = dpg.get_value("length_slider")
    linewidth = dpg.get_value("width_slider")
    zoom = dpg.get_value("zoom_slider")
    ox = dpg.get_value("pan_x")
    oy = dpg.get_value("pan_y")

    rules = parse_rules(rules_text)
    seq = expand_lsystem(axiom, rules, iters)
    lines = interpret_and_get_lines(seq, angle, length)

    # compute bounding box of lines
    if not lines:
        return
    xs = [p[0] for seg in lines for p in seg]
    ys = [p[1] for seg in lines for p in seg]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    width = maxx - minx if maxx != minx else 1.0
    height = maxy - miny if maxy != miny else 1.0

    # determine scale to fit into draw area
    canvas_w, canvas_h = DRAW_W, DRAW_H
    # base_scale tries to fit drawing inside canvas with margins
    margin = 40
    base_scale = min((canvas_w - margin) / width, (canvas_h - margin) / height)
    scale = base_scale * zoom

    # center translation
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0

    # transform function: world coords -> screen coords
    def to_screen(px, py):
        sx = (px - cx) * scale + canvas_w / 2.0 + ox
        sy = (py - cy) * -scale + canvas_h / 2.0 + oy  # flip Y
        return sx, sy

    # clear drawlist
    dpg.delete_item(drawlist_tag, children_only=True)

    # draw lines
    color = (200, 200, 255, 255)
    for a, b in lines:
        x1, y1 = to_screen(a[0], a[1])
        y1_flip = canvas_h - y1 # Invert Y-axis for drawing on the screen, if necessary for desired orientation
        x2, y2 = to_screen(b[0], b[1])
        y2_flip = canvas_h - y2
        
        # NOTE: dpg coordinates start from top-left. 
        # The L-System logic uses a traditional math coordinate system (Y up).
        # We need to decide where to flip the Y-axis. The original code's to_screen 
        # handles the flip: sy = (py - cy) * -scale + canvas_h / 2.0 + oy 
        # so we use y1, y2 directly as computed.

        dpg.draw_line(parent=drawlist_tag, p1=(x1, y1), p2=(x2, y2), color=color, thickness=linewidth)


# ------------------ main loop hook ------------------

def frame_callback(sender, app_data):
    # check regen flag
    # also check if any relevant slider/input was changed (optional, but good practice)
    if dpg.get_value("_regen"):
        compute_and_draw()
        dpg.set_value("_regen", False)


# initialize drawing with defaults
compute_and_draw()

# set frame callback
dpg.set_frame_callback(1, frame_callback)

# start
dpg.create_viewport(title='L-System Editor (Dear PyGui)', width=1200, height=800)

# setup and show
dpg.setup_dearpygui()
# show viewport
dpg.show_viewport()

# ==================== 调试打印语句 ====================
print("--- 尝试启动 GUI 主循环，脚本将在此处等待窗口关闭 ---") 

# start event loop
dpg.start_dearpygui()

# 在主循环退出（即窗口关闭）之后打印
print("--- GUI 窗口已关闭，脚本正在退出 ---") 
# ====================================================

dpg.destroy_context()