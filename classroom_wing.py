"""Classroom Wing — Basic double-loaded corridor layout.

Site: 300 x 200 ft
Wing: 4 classrooms (2 per side), 8-ft central corridor
"""

from tasc_core.dsl.api import *

# --- Site and Grid ---
boundary(300, 200, units="feet")
grid(4)

# --- Wing Layout ---
# Double-loaded corridor, centered on site
# Wing origin: (116, 60)
# Corridor runs north-south at x=146..154
# Total wing: 68 ft wide (30+8+30) x 64 ft tall (32+32)

# West classrooms
zone("Classroom A", 30, 32, at=(116, 60), program_type="public")
zone("Classroom B", 30, 32, at=(116, 92), program_type="public")

# Central corridor
zone("Corridor", 8, 64, at=(146, 60), program_type="circulation")

# East classrooms
zone("Classroom C", 30, 32, at=(154, 60), program_type="public")
zone("Classroom D", 30, 32, at=(154, 92), program_type="public")

# --- Entry + Support ---
# Entry vestibule at south end of corridor
zone("Entry", 20, 12, at=(140, 46), program_type="public")

# Restrooms flanking the entry
zone("Restrooms", 16, 12, at=(160, 46), program_type="service")
zone("Storage", 14, 12, at=(116, 46), program_type="service")

# --- Report ---
describe()

# --- Export ---
export("3dm", output="classroom_wing.3dm")
export("text", output="classroom_wing.txt")
