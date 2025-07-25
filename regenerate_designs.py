import os
import subprocess

def regenerate_designs():
    print("Regenerating LED holder SVG...")
    subprocess.run(['python', 'cnc_led_holder.py'])
    
    print("Regenerating Kepler grid SVG/PNG...")
    subprocess.run(['python', 'kepler.py'])
    
    print("Designs regenerated with current shared config.")

if __name__ == '__main__':
    regenerate_designs()