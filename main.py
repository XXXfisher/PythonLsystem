import dearpygui.dearpygui as dpg
import math
import random
import json
import os

current_loaded_rules = {}
def generate_l_system(axiom, rules, iterations, Topological_Stochasitic=False):
    current_string = axiom 
    for _ in range(iterations):
        next_string = [] 
        for char in current_string:
            if char in rules:
                rules_data = rules[char]
                
                if isinstance(rules_data, str):
                    next_string.append(rules_data)
                
                elif isinstance(rules_data, list):
                    if not rules_data:
                        next_string.append(char)
                        continue
                        
                    if isinstance(rules_data[0], list): 
                        if Topological_Stochasitic:
                            successors = [r[0] for r in rules_data]
                            probabilities = [r[1] for r in rules_data]
                            
                            total_prob = sum(probabilities)
                            if total_prob > 0:
                                norm_probs = [p/total_prob for p in probabilities]
                                chosen = random.choices(successors, weights=norm_probs, k=1)[0]
                                next_string.append(chosen)
                            else:
                                next_string.append(successors[0])
                        else:
                            next_string.append(rules_data[0][0])
                    else:
                         next_string.append(str(rules_data[0]))

            else:
                next_string.append(char)
                
        current_string = "".join(next_string)
    return current_string

def simple_leaf_callback():
    dpg.set_value("##draw_leaf_checkbox", False)
    
    draw_l_system_callback(None, None, None)

def interpret_l_system(l_system_string, angle, length, start_pos, Fluctuation=False):
    
    x, y = start_pos
    heading = math.radians(-90)
    lines = []
    stack = []
    leaves = []
    
    for command in l_system_string:
        angle_variation = angle
        length_variation = length

        if Fluctuation:
            length_variation = length * random.uniform(0.4, 1.2)
            angle_variation = angle * random.uniform(0.4, 1.2)
        
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
            leaves.append((x, y))
            x, y, heading = stack.pop()

    return lines, leaves

#-----------Configuration File------------------
def load_config_from_file(filename):
    filepath = os.path.join("configs", filename)
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {filepath}.")
        return None

def load_preset(json_filename):
    global current_loaded_rules
    p = load_config_from_file(json_filename)
    
    if p:
        current_loaded_rules = p["rules"] 

        dpg.set_value("##axiom_input", p["axiom"])
        rule_f = p["rules"].get("F", [["", 0]])[0][0]
        rule_x = p["rules"].get("X", [["", 0]])[0][0]
        
        dpg.set_value("##rule_input_f", rule_f)
        dpg.set_value("##rule_input_x", rule_x)
        
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

    is_fluctuation = dpg.get_value("##Fluctuation_checkbox") 
    is_stochastic = dpg.get_value("##Stochastic_checkbox")
    is_leaf = dpg.get_value("##Leaf_checkbox")

    rule_f_text = dpg.get_value("##rule_input_f")
    rule_x_text = dpg.get_value("##rule_input_x")

    #two rules: Deterministic and Stochastic
    global current_loaded_rules
    rules = {}
    if is_stochastic and current_loaded_rules:
        rules = current_loaded_rules
    else:

        if rule_f_text:
            rules["F"] = [[rule_f_text, 1.0]] 
        
        if rule_x_text:
            rules["X"] = [[rule_x_text, 1.0]]
    
  
    dpg.delete_item("##drawlist_tag", children_only=True)

    try: 
        l_system_string = generate_l_system(axiom, rules, iterations, Topological_Stochasitic=is_stochastic)

        start_x = 500
        start_y = 600

        lines_data, leaves = interpret_l_system(l_system_string, angle, length, (start_x, start_y), Fluctuation=is_fluctuation)

        dpg.draw_text((10, 10), f"L-System string length: {len(l_system_string)}", parent="##drawlist_tag")
        
        for start_point, end_point in lines_data:
            dpg.draw_line(
                start_point, 
                end_point, 
                color=[0, 150, 255, 255], # Blue color
                thickness=1, 
                parent="##drawlist_tag"
            )
        
        if is_leaf:
            for (lx, ly) in leaves:
                dpg.draw_circle(
                    center=(lx, ly),
                    radius=3,
                    color=[34, 139, 34, 255],  # Green color
                    fill=[34, 139, 34, 200],
                    parent="##drawlist_tag"
                )

    except Exception as e:
        print(f"Python Error: {e}") 
        
        dpg.draw_text(
            pos=(10, 20), 
            text=f"Error: {e}", 
            color=[255, 0, 0, 255], 
            size=20,
            parent="##drawlist_tag"
        )

#-----------SETUP GUI------------------
def setup_gui():
    dpg.create_context()
    dpg.create_viewport(title='L-System', width=1050, height=900)
    dpg.show_metrics()
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
             dpg.add_button(label="Preset A", callback=lambda: load_preset("presetA.json"))
             dpg.add_button(label="Preset B", callback=lambda: load_preset("presetB.json"))
             dpg.add_button(label="Preset C", callback=lambda: load_preset("presetC.json"))
             dpg.add_button(label="Preset D", callback=lambda: load_preset("presetD.json"))
             dpg.add_button(label="Preset E", callback=lambda: load_preset("presetE.json"))
             dpg.add_button(label="Preset F", callback=lambda: load_preset("presetF.json"))
             dpg.add_button(label="Preset G", callback=lambda: load_preset("presetG.json"))
             dpg.add_button(label="Koch curve", callback=lambda: load_preset("koch_curve.json"))
        
         with dpg.child_window(width=300, height=200):   
            dpg.add_text("Features")
            dpg.add_separator()
            dpg.add_checkbox(label="Stochastic Mode", tag="##Stochastic_checkbox", callback=draw_l_system_callback)
            dpg.add_text("(Available for Preset A)", color=[150, 150, 150], wrap=280)

            dpg.add_separator()
            dpg.add_checkbox(label="Fluctuation Mode", tag="##Fluctuation_checkbox", callback=draw_l_system_callback)
            dpg.add_text("(Randomizes angle & length)", color=[150, 150, 150], wrap=280)
            
            dpg.add_separator()
            dpg.add_checkbox(label="Leaf", tag="##Leaf_checkbox", callback=draw_l_system_callback)
            dpg.add_text("(Adds leaves to the plant)", color=[150, 150, 150], wrap=280)

            
        # Use child_window to wrap drawlist
        with dpg.child_window(width=1000, height=700):
            dpg.add_text("Press keys 1-8 to load presets respectively")
            dpg.add_text("Press the button below or space to draw the L-System")
            dpg.add_button(label="Draw L-System", callback=draw_l_system_callback)
            with dpg.drawlist(width=1000, height=750,tag="##drawlist_tag"):
                pass
    
    with dpg.handler_registry():

        dpg.add_key_press_handler(dpg.mvKey_1, callback=lambda: load_preset("presetA.json"))
        dpg.add_key_press_handler(dpg.mvKey_2, callback=lambda: load_preset("presetB.json"))
        dpg.add_key_press_handler(dpg.mvKey_3, callback=lambda: load_preset("presetC.json"))
        dpg.add_key_press_handler(dpg.mvKey_4, callback=lambda: load_preset("presetD.json"))
        dpg.add_key_press_handler(dpg.mvKey_5, callback=lambda: load_preset("presetE.json"))
        dpg.add_key_press_handler(dpg.mvKey_6, callback=lambda: load_preset("presetF.json"))
        dpg.add_key_press_handler(dpg.mvKey_7, callback=lambda: load_preset("presetG.json"))
        dpg.add_key_press_handler(dpg.mvKey_8, callback=lambda: load_preset("koch_curve.json"))
        
        dpg.add_key_press_handler(dpg.mvKey_Spacebar, callback=draw_l_system_callback)

    print("window setup complete...")
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
     
if __name__ == "__main__":
    setup_gui()



