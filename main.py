import dearpygui.dearpygui as dpg
import math
import random


#------------presets----------------
def generate_l_system(axiom, rules, iterations):
    current_string = axiom
    for _ in range(iterations):
        next_string = []
        for char in current_string:
            next_string.append(rules.get(char, char))
        current_string = "".join(next_string)
    return current_string


def interpret_l_system(l_system_string, angle, length, start_pos, stochastic=False):
    
    x, y = start_pos
    heading = math.radians(-90)
    lines = []
    stack = []
    

    for command in l_system_string:
        # current_length = length
        angle_variation = angle
        length_variation = length

        if stochastic:
            length_variation = length * random.uniform(0.8, 1.2)
            angle_variation = angle * random.uniform(0.8, 1.2)
        
        if command == "F":
            new_x = x + length_variation*math.cos(heading)
            new_y = y + length_variation*math.sin(heading)
            lines.append(((x, y), (new_x, new_y)))
            x, y = new_x, new_y
        elif command == "+":
            heading -= math.radians(angle_variation)
        elif command == "-":
            heading += math.radians(angle_variation)
        elif command == "[":
            stack.append((x, y, heading))
        elif command == "]":
            x, y, heading = stack.pop()

    return lines

#------------presets----------------
preset = {
    "presetA": {
    "axiom": "F",
    "rules": {"F": "F[+F]F[-F]F"},
    "angle": 25.7,
    "iterations": 5,
    "length": 2,
},
    "presetB": {
    "axiom": "F",
    "rules": {"F": "F[+F]F[-F][F]"},
    "angle": 20,
    "iterations": 5,
    "length": 10,
},
    "presetC": {
    "axiom": "F",
    "rules": {"F": "FF-[-F+F+F]+[+F-F-F]"},
    "angle": 22.5,
    "iterations": 4,
    "length": 10,
},
    "presetD": {
    "axiom": "X",
    "rules": {"X": "F[+X]F[-X]+X", "F": "FF"},
    "angle": 20,
    "iterations": 7,
    "length": 2,
},
    "presetE": {
    "axiom": "X",
    "rules": {"X": "F[+X][-X]FX", "F": "FF"},
    "angle": 25.7,
    "iterations": 7,
    "length": 2,
},    
    "presetF": {
    "axiom": "X",
    "rules": {"X": "F-[[X]+X]+F[+FX]-X", "F": "FF"},
    "angle": 22.5,
    "iterations": 5,
    "length": 5,
},    
    "presetG": {
    "axiom": "F++F++F++F++F",
    "rules": {"F": "F++F++F+++++F-F++F"},
    "angle": 36,
    "iterations": 4,
    "length": 2,
},
    "Koch curve": {
    "axiom": "F++F++F",
    "rules": {"F": "F-F++F-F"},
    "angle": 60,
    "iterations": 4,
    "length": 2,
}
}
def load_preset(preset_name):
    if preset_name in preset:
        p = preset[preset_name]
        dpg.set_value("##axiom_input", p["axiom"])
        dpg.set_value("##rule_input_f", p["rules"].get("F", ""))
        dpg.set_value("##rule_input_x", p["rules"].get("X", ""))
        dpg.set_value("##angle_slider", p["angle"])
        dpg.set_value("##iterations_slider", p.get("iterations", 4))
        dpg.set_value("##length_slider", p["length"])
    return


#-----------CALLBACK------------------
def draw_l_system_callback(sender, app_data, user_data):

    axiom = dpg.get_value("##axiom_input")
    iterations = dpg.get_value("##iterations_slider")
    angle = dpg.get_value("##angle_slider")
    length = dpg.get_value("##length_slider")

    is_stochastic = dpg.get_value("##stochastic_checkbox") 

    rules = {
        "F": dpg.get_value("##rule_input_f"), 
        "X": dpg.get_value("##rule_input_x")
        }

    dpg.delete_item("##drawlist_tag", children_only=True)

    try: 
        l_system_string = generate_l_system(axiom, rules, iterations)

        start_x = 500
        start_y = 600
        lines_data = interpret_l_system(l_system_string, angle, length, (start_x, start_y), stochastic=is_stochastic)

        dpg.draw_text((10, 10), f"L-System string length: {len(l_system_string)}", parent="##drawlist_tag")
        
        for start_point, end_point in lines_data:
            dpg.draw_line(
                start_point, 
                end_point, 
                color=[0, 150, 255, 255], # Blue color
                thickness=1, 
                parent="##drawlist_tag"
            )

    except Exception as e:
        dpg.add_text(f"Error in L-system generation: {e}", parent="##drawlist_tag")

def setup_gui():
    dpg.create_context()
    dpg.create_viewport(title='L-System', width=1050, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()   

    with dpg.window(tag="Primary Window", label="L-System Drawer", width=1050, height=900):
        with dpg.group(horizontal=True):
         with dpg.child_window(width=600, height=200):
          dpg.add_text("Basic L-System Parameters:")
          dpg.add_input_text(label="Axiom", default_value="F", tag="##axiom_input", width=500)
          dpg.add_input_text(label="Rule F", tag="##rule_input_f", width=500)
          dpg.add_input_text(label="Rule X", tag="##rule_input_x", width=500)
          dpg.add_slider_int(label="Iterations", default_value=4, min_value=1, max_value=6, tag="##iterations_slider", width=500)
          dpg.add_slider_int(label="Angle", default_value=25, min_value=0, max_value=90, tag="##angle_slider", width=500)
          dpg.add_slider_int(label="Length", default_value=5, min_value=1, max_value=20, tag="##length_slider", width=500)
        
         with dpg.child_window(width=90, height=200):
             dpg.add_button(label="Preset A", callback=lambda:load_preset("presetA"))
             dpg.add_button(label="Preset B", callback=lambda:load_preset("presetB"))
             dpg.add_button(label="Preset C", callback=lambda:load_preset("presetC"))
             dpg.add_button(label="Preset D", callback=lambda:load_preset("presetD"))
             dpg.add_button(label="Preset E", callback=lambda:load_preset("presetE"))
             dpg.add_button(label="Preset F", callback=lambda:load_preset("presetF"))
             dpg.add_button(label="Preset G", callback=lambda:load_preset("presetG"))
             dpg.add_button(label="Koch curve", callback=lambda:load_preset("Koch curve"))
        
         with dpg.child_window(width=300, height=200):   
            dpg.add_text("Features")
            dpg.add_separator()
            dpg.add_checkbox(label="Stochastic Mode", tag="##stochastic_checkbox", callback=draw_l_system_callback)
            dpg.add_text("(Randomizes angle & length)", color=[150, 150, 150], wrap=280)

        # Use child_window to wrap drawlist
        with dpg.child_window(width=1000, height=700):
            dpg.add_text("Press the button below to draw the L-System")
            dpg.add_button(label="Draw L-System", callback=draw_l_system_callback)
            with dpg.drawlist(width=1000, height=750,tag="##drawlist_tag"):
                pass


    print("window setup complete...")
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
     
if __name__ == "__main__":
    setup_gui()



