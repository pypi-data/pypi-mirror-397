from mcshell.mcplayer import MCPlayer
from mcshell.constants import *

from mcshell.mcvoxel_original import (
    generate_digital_tetrahedron_coordinates,
    generate_digital_tube_coordinates,
    generate_digital_plane_coordinates,
    generate_digital_ball_coordinates,
    generate_digital_cube_coordinates,
    generate_digital_disc_coordinates,
    generate_digital_line_coordinates,
    generate_digital_sphere_coordinates
)

# Advanced Digital Geometry and Turtle
from mcshell.mcturtle import (
    DigitalTurtle,
    generate_metric_ball,
    generate_digital_plane_coordinates as generate_arithmetic_plane,
    generate_linear_path,
    DigitalSet
)

# L-System Logic
from mcshell.mclsystem import LSystem

from blockapily import mced_block

# Global turtle instance
_GLOBAL_TURTLE = DigitalTurtle()

class MCActionsBase:
    def __init__(self, mc_player_instance:MCPlayer,delay_between_blocks:float): # Added mc_version parameter
        """
        Initializes the action base.

        Args:
            mc_player_instance: An instance of a player connection class (e.g., MCPlayer).
            mc_version (str): The Minecraft version to load data for. This should match
                              the version of the server you are connecting to.
        """
        self.mcplayer = mc_player_instance

        # Initialize mapping dictionaries
        self.bukkit_to_entity_id_map = {}
        self._initialize_entity_id_map()

        # allow a delay for between visuals
        self.delay_between_blocks = delay_between_blocks

    def _place_blocks_from_coords(self, coords_list, block_type_from_blockly,
                                  placement_offset_vec3=None):
        """
        Helper method to take a list of coordinates and a Blockly block type,
        parse the block type, and set the blocks.
        """
        if not coords_list:
            print("No coordinates generated, nothing to place.")
            return

        # we use Bukkit IDs which are output in mc-ed
        minecraft_block_id = block_type_from_blockly

        # print(f"Attempting to place {len(coords_list)} blocks of type '{minecraft_block_id}'")

        offset_x, offset_y, offset_z = (0,0,0)
        if placement_offset_vec3: # If a Vec3 object is given for overall placement
            offset_x, offset_y, offset_z = int(placement_offset_vec3.x), int(placement_offset_vec3.y), int(placement_offset_vec3.z)

        for x, y, z in coords_list:

            final_x = x + offset_x
            final_y = y + offset_y
            final_z = z + offset_z
            self.mcplayer.pc.setBlock(int(final_x), int(final_y), int(final_z), minecraft_block_id)

            # Pause execution for a fraction of a second
            if self.delay_between_blocks > 0:
                time.sleep(self.delay_between_blocks)

        # print(f"Placed {len(coords_list)} blocks.")

    def _place_digital_set(self, dset: DigitalSet, block_type):
        """
        Helper to render a DigitalSet into the world.
        """
        if not dset: return
        coords = dset.to_list()
        self._place_blocks_from_coords(coords, block_type)

    def _initialize_entity_id_map(self):
        with MC_ENTITY_ID_MAP_PATH.open('rb') as f:
            self.bukkit_to_entity_id_map = pickle.load(f)

    def _get_entity_id_from_bukkit_name(self, bukkit_enum_string: str) -> Optional[int]:
        """
        Converts a Bukkit enum string (e.g., 'WITHER_SKELETON') to its Minecraft numeric ID.

        Args:
            bukkit_enum_string: The uppercase, underscore-separated entity name.

        Returns:
            The integer ID of the entity, or None if not found.
        """
        # Use .get() for a safe lookup that returns None if the key doesn't exist
        return self.bukkit_to_entity_id_map.get(bukkit_enum_string)

class Pickers:
    """Registry of custom picker options for blocks."""

    Metric = [
        ("Euclidean (Sphere)", "euclidean"),
        ("Manhattan (Diamond)", "manhattan"),
        ("Chebyshev (Cube)", "chebyshev")
    ]

    Direction = [
        ("Forward", "forward"), ("Back", "back"),
        ("Up", "up"), ("Down", "down"),
        ("Left", "left"), ("Right", "right")
    ]

    Axis = [
        ("Yaw (Y)", "y"), ("Pitch (X)", "x"), ("Roll (Z)", "z")
    ]

    Compass = [
        ("North (-Z)", "N"), ("South (+Z)", "S"),
        ("East (+X)", "E"), ("West (-X)", "W"),
        ("North-East", "NE"), ("North-West", "NW"),
        ("South-East", "SE"), ("South-West", "SW")
    ]

class TurtleShapes(MCActionsBase):
    """
    Value Blocks: These generate DigitalSet objects but do not change the world state.
    """
    def __init__(self, mc_player_instance, delay_between_blocks=0.01):
        super().__init__(mc_player_instance, delay_between_blocks)  # Call parent constructor

    @mced_block(
        label="Digital Shape: Sphere/Diamond/Cube",
        radius={'label': 'Radius', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        metric={'label': 'Metric'}, # Needs Dropdown definition in Blockly
        output_type="Digital_Set",
        tooltip="Creates a mathematical shape. Does not place blocks."
    )
    def get_metric_ball(self, radius: int, metric: 'Metric') -> DigitalSet:
        return generate_metric_ball((0,0,0), radius, metric)

    @mced_block(
        label="Digital Shape: Arithmetic Plane (Square)",
        normal={'label': 'Normal'},
        side_length={'label': 'Side Length', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        output_type="Digital_Set",
        tooltip="Creates a square digital plane using the arithmetic definition."
    )
    def get_arithmetic_plane(self, normal: 'Vec3', side_length: int) -> DigitalSet:
        # Center is 0,0,0 relative to the shape origin
        # Creates a square plane by using side_length for both width and height
        return generate_arithmetic_plane(
            normal.to_tuple(), (0,0,0), (side_length, side_length)
        )

    @mced_block(
        label="Digital Shape: Line",
        p1={'label': 'point_1'},
        p2={'label': 'point_2'},
        output_type='Digital_Set',
        tooltip="Create a digital line using arithmetic definition"
    )
    def get_line(self,p1:'Vec3',p2:'Vec3') -> DigitalSet:
        return generate_linear_path(p1.to_tuple(),p2.to_tuple())

def _check_turtle_state(t,action='move'):
    ic(action)
    ic(t.pos)
    ic(t.right)
    ic(t.up)
    ic(t.forward)

class TurtleActions(MCActionsBase):
    """
    Statement Blocks: These control the Turtle state or modify the world.
    """

    def __init__(self, mc_player_instance, delay_between_blocks=0.01):
        super().__init__(mc_player_instance, delay_between_blocks)  # Call parent constructor
        self.turtle = _GLOBAL_TURTLE

    # --- TURTLE CONTROL ---
    @mced_block(
        label="Turtle: Reset to",
        position={'label': 'Position', },
        orientation={'label': 'Facing'},
        tooltip="Resets turtle to position and cardinal orientation."
    )
    def turtle_reset(self, position: 'Vec3', orientation: 'Compass' = 'N'):
        # 1. Handle Position
        if position:
            x, y, z = position.x, position.y, position.z
        else:
            pos = self.player.get_position()
            x, y, z = pos.x, pos.y, pos.z

        self.turtle.pos = np.array([int(x), int(y), int(z)], dtype=int)

        # 2. Handle Orientation (Cardinal Basis Vectors)
        # Up is always +Y for reset
        self.turtle.up = np.array([0,1,0], dtype=int)

        # Define Basis Map: (Forward, Right)
        # North (-Z) -> Forward=(0,0,-1), Right=(1,0,0)
        # South (+Z) -> Forward=(0,0,1),  Right=(-1,0,0)
        # East (+X)  -> Forward=(1,0,0),  Right=(0,0,1)
        # West (-X)  -> Forward=(-1,0,0), Right=(0,0,-1)

        orientation = orientation.upper()

        if orientation == 'N':
            self.turtle.forward = np.array([0,0,-1], dtype=int)
            self.turtle.right   = np.array([1,0,0], dtype=int)
        elif orientation == 'S':
            self.turtle.forward = np.array([0,0,1], dtype=int)
            self.turtle.right   = np.array([-1,0,0], dtype=int)
        elif orientation == 'E':
            self.turtle.forward = np.array([1,0,0], dtype=int)
            self.turtle.right   = np.array([0,0,1], dtype=int)
        elif orientation == 'W':
            self.turtle.forward = np.array([-1,0,0], dtype=int)
            self.turtle.right   = np.array([0,0,-1], dtype=int)

        # Diagonals (45 degree basis logic is complex on integer grid for Turtle Reset)
        # For simplicity in a reset, we snap to nearest Cardinal, or implement diagonal basis
        # if DigitalTurtle supports non-axis-aligned basis vectors (it does).
        elif orientation == 'NE':
            self.turtle.forward = np.array([1,0,-1], dtype=int) # Diagonal Fwd
            self.turtle.right   = np.array([1,0,1], dtype=int)  # Diagonal Right
        elif orientation == 'NW':
            self.turtle.forward = np.array([-1,0,-1], dtype=int)
            self.turtle.right   = np.array([1,0,-1], dtype=int)
        elif orientation == 'SE':
            self.turtle.forward = np.array([1,0,1], dtype=int)
            self.turtle.right   = np.array([-1,0,1], dtype=int)
        elif orientation == 'SW':
            self.turtle.forward = np.array([-1,0,1], dtype=int)
            self.turtle.right   = np.array([-1,0,-1], dtype=int)
        else:
            # Default North
            self.turtle.forward = np.array([0,0,-1], dtype=int)
            self.turtle.right   = np.array([1,0,0], dtype=int)

        self.turtle.stack = []

    @mced_block(
        label="Turtle: Move",
        direction={'label': 'Direction'},
        distance={'label': 'Distance', 'shadow': '<shadow type="math_number"><field name="NUM">1</field></shadow>'}
    )
    def turtle_move(self, direction: 'Direction', distance: int):
        self.turtle.move(distance, direction)

    @mced_block(
        label="Turtle: Rotate 90",
        axis={'label': 'Axis'},
        steps={'label': 'Steps (90 deg)', 'shadow': '<shadow type="math_number"><field name="NUM">1</field></shadow>'}
    )
    def turtle_rotate(self, axis: 'Axis', steps: int):
        self.turtle.rotate_90(axis, steps)

    @mced_block(
        label="Turtle: Shear",
        primary={'label': 'Primary Axis'},
        secondary={'label': 'Shear By Axis'},
        factor={'label': 'Factor', 'shadow': '<shadow type="math_number"><field name="NUM">1</field></shadow>'}
    )
    def turtle_shear(self, primary: 'Axis', secondary: 'Axis', factor: int):
        self.turtle.shear(primary, secondary, factor)

    @mced_block(
        label="Turtle: Push State"
    )
    def turtle_push(self):
        self.turtle.push_state()

    @mced_block(
        label="Turtle: Pop State"
    )
    def turtle_pop(self):
        self.turtle.pop_state()

    # --- BRUSH & DRAWING ---

    @mced_block(
        label="Turtle: Set Brush",
        shape={'label': 'Shape', 'check': 'Digital_Set'}
    )
    def turtle_set_brush(self, shape: DigitalSet):
        self.turtle.set_brush(shape)

    @mced_block(
        label="Turtle: Stamp Brush",
        block_type={'label': 'Material'}
    )
    def turtle_stamp(self, block_type: 'Block'):
        shape = self.turtle.stamp()
        self._place_digital_set(shape, block_type)

    @mced_block(
        label="Turtle: Extrude Brush",
        length={'label': 'Length', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        block_type={'label': 'Material'}
    )
    def turtle_extrude(self, length: int, direction: 'Direction', block_type: 'Block'):
        shape = self.turtle.extrude(length,direction)
        self._place_digital_set(shape, block_type)

    # --- STATIC BRIDGE ---

    @mced_block(
        label="Construct Shape at Player",
        shape={'label': 'Shape', 'check': 'Digital_Set'},
        block_type={'label': 'Material' },
        tooltip="Places a digital shape at the player's current location."
    )
    def place_static_shape(self, shape: DigitalSet, block_type: 'Block'):
        # Translate shape to player position
        pos = self.player.get_position()
        # Ensure integer translation
        moved_shape = shape.translate(int(pos.x), int(pos.y), int(pos.z))
        self._place_digital_set(moved_shape, block_type)

class LSystemShapes(MCActionsBase):
    """
    Exposes L-System grammar logic for procedural generation as a DigitalSet.
    """
    def __init__(self, player):
        super().__init__(player)
        # We need a temporary turtle for interpreting the L-system symbols into a shape
        # This turtle is local to the generation process and doesn't affect the global turtle
        self.local_turtle = DigitalTurtle()

    @mced_block(
        label="L-System: Define Rule",
        predecessor={'label': 'Symbol (char)', 'shadow': 'text'},
        successor={'label': 'Replacement', 'shadow': 'text'},
        output_type="LSYSTEM_RULE", # Custom type for rule tuple
        tooltip="Defines a rewrite rule: A -> AB"
    )
    def define_rule(self, predecessor: str, successor: str):
        # Return a tuple or dict representing the rule
        return (predecessor, successor)

    @mced_block(
        label="L-System: Generate Shape",
        axiom={'label': 'Axiom', 'shadow': 'text'},
        iterations={'label': 'Iterations', 'shadow': '<shadow type="math_number"><field name="NUM">3</field></shadow>'},
        step_length={'label': 'Step Length', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        # rules list
        rules={'label': 'Rules (List)', 'check': 'Array'},
        output_type="Digital_Set",
        tooltip="Generates a shape from an L-System grammar."
    )
    def get_lsystem_shape(self, axiom: str, iterations: int, step_length: int, rules: list) -> DigitalSet:
        # 1. Parse Rules list into Dict
        rule_dict = {}
        if rules:
            for r in rules:
                if len(r) >= 2:
                    rule_dict[r[0]] = r[1]

        # 2. Run L-System Logic
        lsys = LSystem(axiom, rule_dict)
        final_string = lsys.iterate(int(iterations))

        # 3. Interpret with Local Turtle
        # Reset local turtle to origin for shape generation
        self.local_turtle.pos = np.array([0,0,0], dtype=int)
        self.local_turtle.forward = np.array([0,0,1], dtype=int) # Default Forward
        self.local_turtle.up = np.array([0,1,0], dtype=int)
        self.local_turtle.right = np.array([1,0,0], dtype=int)
        self.local_turtle.brush = DigitalSet()
        self.local_turtle.brush.add((0,0,0))
        self.local_turtle.stack = []

        accumulated_shape = DigitalSet()

        for char in final_string:
            shape_segment = self.local_turtle.interpret_symbol(char, int(step_length))
            if shape_segment:
                accumulated_shape = accumulated_shape.union(shape_segment)

        return accumulated_shape

class DigitalGeometry(MCActionsBase):
    """
    Actions that involve creating geometric shapes.
    """
    def __init__(self, mc_player_instance,delay_between_blocks=0.01):
        super().__init__(mc_player_instance,delay_between_blocks) # Call parent constructor
        self.default_material_id = 1 # Example: material ID for stone in voxelmap
                                 # Or map block_type to material_id

    @mced_block(
        label="Create Digital Cube",
        center={'label': 'Center'},
        side_length={'label': 'Side Length', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        rotation_matrix={'label': 'Rotation Matrix', 'shadow': '<shadow type="minecraft_matrix_3d_euler"></shadow>'},
        block_type={'label': 'Block Type'},
        wall_thickness={'label': 'Wall Thickness (0=solid)', 'shadow': '<shadow type="math_number"><field name="NUM">0</field></shadow>'}
    )
    def create_digital_cube(self,
                          center: 'Vec3',
                          side_length: float,
                          rotation_matrix: 'Matrix3',
                          block_type: 'Block',
                          wall_thickness: float = 0.0):
        """
        Blockly action to create a digital cube.
        """
        coords = generate_digital_cube_coordinates(
            center=center.to_tuple(),
            side_length=float(side_length),
            rotation_matrix=rotation_matrix.to_numpy(),
            wall_thickness=float(wall_thickness)
        )
        self._place_blocks_from_coords(coords, block_type)

    @mced_block(
        label="Create Digital Line",
        point1={'label': 'Start Point'},
        point2={'label': 'End Point'},
        block_type={'label': 'Block Type'}
    )
    def create_digital_line(self, point1: 'Vec3', point2: 'Vec3', block_type: 'Block'):
        coords = generate_digital_line_coordinates(
            p1=point1.to_tuple(),
            p2=point2.to_tuple()
        )
        self._place_blocks_from_coords(coords, block_type)

    @mced_block(
        label="Create Digital Plane",
        center={'label': 'Center'},
        normal={'label': 'Normal'},
        side_length={'label': 'Side Length', 'shadow': '<shadow type="math_number"><field name="NUM">10</field></shadow>'},
        block_type={'label': 'Block Type'}
    )
    def create_digital_plane(self, center: 'Vec3', normal: 'Vec3', side_length: float, block_type: 'Block'):
        coords = generate_digital_plane_coordinates(
            point_on_plane=center.to_tuple(),
            normal=normal.to_tuple(),
            outer_rect_dims=(side_length,side_length)
        )
        self._place_blocks_from_coords(coords, block_type)

    @mced_block(
        label="Create Digital Disc",
        center={'label': 'Center' },
        normal={'label': 'Normal'},
        radius={'label': 'Radius', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        block_type={'label': 'Block Type'}
    )
    def create_digital_disc(self, center: 'Vec3', normal: 'Vec3', radius: float, block_type: 'Block'):
        coords = generate_digital_disc_coordinates(
            center_point=center.to_tuple(),
            normal=normal.to_tuple(),
            outer_radius=radius
        )
        self._place_blocks_from_coords(coords, block_type)

    @mced_block(
        label="Create Digital Sphere",
        center={'label': 'Center'},
        radius={'label': 'Radius', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        block_type={'label': 'Block Type'},
        is_hollow={'label': 'Hollow', 'shadow': '<shadow type="logic_boolean"><field name="BOOL">FALSE</field></shadow>'}
    )
    def create_digital_sphere(self, center: 'Vec3', radius: int, block_type: 'Block', is_hollow: bool):
        coords = generate_digital_sphere_coordinates(
            center=center.to_tuple(),
            radius=int(radius),
            is_solid=not is_hollow
        )
        self._place_blocks_from_coords(coords, block_type)

    @mced_block(
        label="Create Digital Ball",
        center={'label': 'Center'},
        radius={'label': 'Radius', 'shadow': '<shadow type="math_number"><field name="NUM">5</field></shadow>'},
        block_type={'label': 'Block Type'}
    )
    def create_digital_ball(self, center: 'Vec3', radius: int, block_type: 'Block'):
        coords = generate_digital_ball_coordinates(
            center=center.to_tuple(),
            radius=int(radius)
        )
        self._place_blocks_from_coords(coords, block_type)

    @mced_block(
        label="Create Digital Tube",
        start={'label': 'Start'},
        end={'label': 'End'},
        radius={'label': 'Radius', 'shadow': '<shadow type="math_number"><field name="NUM">3</field></shadow>'},
        block_type={'label': 'Block Type'},
        is_hollow={'label': 'Hollow', 'shadow': '<shadow type="logic_boolean"><field name="BOOL">TRUE</field></shadow>'}
    )
    def create_digital_tube(self, start: 'Vec3', end: 'Vec3', radius: float, block_type: 'Block', is_hollow: bool):
        if is_hollow:
            inner_thickness = 1.0
        else:
            inner_thickness = 0.0

        coords = generate_digital_tube_coordinates(
            p1=start.to_tuple(),
            p2=end.to_tuple(),
            outer_thickness=radius,
            inner_thickness=inner_thickness,
        )
        self._place_blocks_from_coords(coords, block_type)

    @mced_block(
        label="Create Digital Tetrahedron",
        p1={'label': 'Point 1'},
        p2={'label': 'Point 2'},
        p3={'label': 'Point 3'},
        p4={'label': 'Point 4'},
        inner_offset_factor={'label': 'Inner Offset Factor','shadow':'<shadow type="math_number"><field name="NUM">3</field></shadow>'},
        block_type={'label': 'Block Type'}
    )
    def create_digital_tetrahedron(self, p1:'Vec3',p2:'Vec3',p3:'Vec3',p4:'Vec3',inner_offset_factor:float,block_type: 'Block'):
        coords = generate_digital_tetrahedron_coordinates(
            vertices=[p1.to_tuple(),p2.to_tuple(),p3.to_tuple(),p4.to_tuple()],
            inner_offset_factor=inner_offset_factor,
        )
        self._place_blocks_from_coords(coords, block_type)

class WorldActions(MCActionsBase):
    def __init__(self, mc_player_instance, delay_between_blocks=0):
        super().__init__(mc_player_instance, delay_between_blocks)
        self.default_material_id = 1

    @mced_block(
        label="Spawn Entity",
        entity={'label': 'Entity Type'},
        position={'label': 'At Position'}
    )
    def spawn_entity(self, position: 'Vec3', entity: 'Entity'):
        """
        Blockly action to spawn a Minecraft entity.
        """
        entity_id_int = self._get_entity_id_from_bukkit_name(entity)
        if entity_id_int is None:
            print(f"Warning: Could not find a numerical ID for entity type '{entity}'. Cannot spawn.")
            return
        self.mcplayer.pc.spawnEntity(position.x, position.y + 1, position.z, entity_id_int)

    @mced_block(
        label="Set Block",
        position={'label': 'At Position'},
        block_type={'label': 'Block Type'}
    )
    def set_block(self, position: 'Vec3', block_type: 'Block'):
        """
        Blockly action to set a single block in the Minecraft world.
        """
        x, y, z = (int(position.x), int(position.y), int(position.z))
        self.mcplayer.pc.setBlock(x, y, z, block_type)

    @mced_block(
        label="Set Blocks",
        position_1={'label': 'Position 1'},
        position_2={'label': 'Position 2'},
        block_type={'label': 'Block Type'}
    )
    def set_blocks(self,position_1: 'Vec3',position_2: 'Vec3',block_type):
        """
        Blockly action to set a cuboid of blocks in the Minecraft world.
        """
        x1, y1, z1 = int(position_1.x), int(position_1.y), int(position_1.z)
        x2, y2, z2 = int(position_2.x), int(position_2.y), int(position_2.z)
        self.mcplayer.pc.setBlocks(x1,y1,z1,x2,y2,z2,block_type)

    @mced_block(
        label="Get Block",
        output_type="Block",
        position={'label': 'At Position'}
    )
    def get_block(self, position: 'Vec3') -> 'Block':
        """
        Gets the block type at a specific location.
        """
        x, y, z = (int(position.x), int(position.y), int(position.z))
        block_type = self.mcplayer.pc.getBlock(x, y, z)
        return block_type if block_type else 'AIR'

    @mced_block(
        label="Get Height",
        output_type="Number",
        position={'label': 'At Position (X,Z)'}
    )
    def get_height(self, position: 'Vec3') -> int:
        """
        Gets the Y coordinate of the highest block at the X,Z of the given position.
        """
        x, z = (int(position.x), int(position.z))
        height = self.mcplayer.pc.getHeight(x, z)
        return int(height)

    @mced_block(
        label="Post to Chat",
        message={'label': 'Message', 'shadow': '<shadow type="text"><field name="TEXT">Hello, World!</field></shadow>'}
    )
    def post_to_chat(self, message: str):
        """
        Posts a message to the in-game chat.
        """
        self.mcplayer.pc.postToChat(str(message))

    @mced_block(
        label="Create Explosion",
        position={'label': 'At Position'},
        power={'label': 'Power', 'shadow': '<shadow type="math_number"><field name="NUM">4</field></shadow>'}
    )
    def create_explosion(self, position: 'Vec3', power: float):
        """
        Creates an explosion at a specific location.
        """
        x, y, z = (float(position.x), float(position.y), float(position.z))
        self.mcplayer.pc.createExplosion(x, y, z, float(power))

class PlayerActions(MCActionsBase):
    def __init__(self, mc_player_instance, delay_between_blocks=0):
        super().__init__(mc_player_instance, delay_between_blocks)

    @mced_block(
        label="Get Player Direction",
        output_type="3DVector"
    )
    def get_direction(self):
        # if we return a value, we must specify output_type
        return self.mcplayer.direction
    @mced_block(
        label="Get Player Position",
        output_type="3DVector"
    )
    def get_position(self):
        return self.mcplayer.position

    @mced_block(
        label="Get Player Tile Position",
        output_type="3DVector"
    )
    def get_tile_position(self):
        return self.mcplayer.tile_position

    @mced_block(
        label="Wait for Sword Strike Position",
        output_type="3DVector"
    )
    def wait_for_sword_strike(self):
        return self.mcplayer.here

    @mced_block(
        label="Get Player Compass Direction",
        output_type="Compass"
    )
    def get_compass_direction(self):
        return self.mcplayer.compass_direction

    @mced_block(
        label="Set Player Compass Direction",
    )
    def set_compass_direction(self, dir: 'Compass'):
        self.mcplayer.set_compass_direction(dir)

    @mced_block(
        label="Set Player Position",
    )
    def set_position(self, pos: 'Vec3'):
        self.mcplayer.set_position(pos)

class MCActions(LSystemShapes,PlayerActions,TurtleShapes,TurtleActions,DigitalGeometry,WorldActions):
    '''Group All APIs for Blockly in a single class'''