"""
Parametric steel hall example using manipulation functions.
"""

from dlubal.api import rstab, common

# Editable parameters (SI units)
FRAME_SPACING = 5.0
FRAME_COUNT = 5
FRAME_WIDTH = 13.0
FRAME_HEIGHT_MIN = 4.5
FRAME_HEIGHT_MAX = 6.0
RAFTER_SLOPE_LENGTH = 0.2
RAFTER_FIELDS = 2

STEEL_GRADE = "S235 | EN 10025-2:2004-11"
SECTION_COLUMN = "IPE 300"
SECTION_RAFTER = "I 0.3/0.11/0.006/0.014/0/0/H"
SECTION_RAFTER_TAPPERED = "I 0.6/0.11/0.006/0.014/0/0/H"
SECTION_PURLINS = "CHC 139.7x8.0"
SECTION_BRACING = "R 20"


def build_frame() -> list:

    inf = float('inf')

    frame_objs = [

        # Material
        rstab.structure_core.Material(no=1, name=STEEL_GRADE),

        # Cross-section
        rstab.structure_core.CrossSection(no=1, name=SECTION_COLUMN, material=1),
        rstab.structure_core.CrossSection(no=2, name=SECTION_RAFTER, material=1),
        rstab.structure_core.CrossSection(no=3, name=SECTION_RAFTER_TAPPERED, material=1),

        # Nodes
        rstab.structure_core.Node(no=1),
        rstab.structure_core.Node(no=2, coordinate_3=-FRAME_HEIGHT_MIN),
        rstab.structure_core.Node(no=3, coordinate_1=FRAME_WIDTH/2, coordinate_3=-FRAME_HEIGHT_MAX),
        rstab.structure_core.Node(no=4, coordinate_1=FRAME_WIDTH, coordinate_3=-FRAME_HEIGHT_MIN),
        rstab.structure_core.Node(no=5, coordinate_1=FRAME_WIDTH),

        # Members
        rstab.structure_core.Member(
            no=1, node_start=1, node_end=2, cross_section_start=1, type=rstab.structure_core.Member.TYPE_BEAM
        ),
        rstab.structure_core.Member(
            no=2, node_start=2, node_end=3, cross_section_start=3, cross_section_end=2,
            type=rstab.structure_core.Member.TYPE_BEAM,
            cross_section_distribution_type=rstab.structure_core.Member.CROSS_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_START_OF_MEMBER,
            cross_section_distance_from_start_is_defined_as_relative=True,
            section_distance_from_start_relative=RAFTER_SLOPE_LENGTH
        ),
        rstab.structure_core.Member(
            no=3, node_start=3, node_end=4, cross_section_start=2, cross_section_end=3,
            type=rstab.structure_core.Member.TYPE_BEAM,
            cross_section_distribution_type=rstab.structure_core.Member.CROSS_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_END_OF_MEMBER,
            cross_section_distance_from_end_is_defined_as_relative=True,
            cross_section_distance_from_end_relative=RAFTER_SLOPE_LENGTH
        ),
        rstab.structure_core.Member(
            no=4, node_start=4, node_end=5, cross_section_start=1, type=rstab.structure_core.Member.TYPE_BEAM
        ),

        # Nodal support (hinge)
        rstab.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1, 5],
            spring_x=inf,
            spring_y=inf,
            spring_z=inf,
            rotational_restraint_z=inf
        ),

    ]

    # Rafter internal nodes for purlins connection
    node_no = 8
    for member_ref in (2, 3):
        for j in range(1, RAFTER_FIELDS):
            frame_objs.append(
                rstab.structure_core.Node(
                    no=node_no,
                    type=rstab.structure_core.Node.TYPE_ON_MEMBER,
                    on_member_reference_member=member_ref,
                    distance_from_start_relative=j / RAFTER_FIELDS,
                )
            )
            node_no += 1


    return frame_objs


def build_purlins() -> list:

    nodes_per_frame = 7 + 2* (RAFTER_FIELDS-1)
    member_no = 4 * FRAME_COUNT

    purlin_objs = [
        rstab.structure_core.CrossSection(no=4, name=SECTION_PURLINS, material=1),
        rstab.structure_core.Member(
            no=member_no+1, node_start=2, node_end=nodes_per_frame+2, cross_section_start=4,
            type=rstab.structure_core.Member.TYPE_TRUSS
        ),
        rstab.structure_core.Member(
            no=member_no+2, node_start=3, node_end=nodes_per_frame+3, cross_section_start=4,
            type=rstab.structure_core.Member.TYPE_TRUSS
        ),
        rstab.structure_core.Member(
            no=member_no+3, node_start=4, node_end=nodes_per_frame+4, cross_section_start=4,
            type=rstab.structure_core.Member.TYPE_TRUSS
        ),
    ]

    member_no += 3

    for j in range(1, RAFTER_FIELDS*2 - 1):
        purlin_objs.extend([
            rstab.structure_core.Member(
                no=member_no+1, node_start=7+j, node_end=nodes_per_frame+7+j, cross_section_start=4,
                type=rstab.structure_core.Member.TYPE_TRUSS
            )
        ])
        member_no += 1

    return purlin_objs

# --- Main function to execute ---
with rstab.Application() as rstab_app:

    # Close all existing models and create a new empty one
    rstab_app.close_all_models(save_changes=False)
    model_id = rstab_app.create_model(name='steel_hall_parametric')
    rstab_app.delete_all_objects()

    # Build the frame
    frame_objs = build_frame()
    rstab_app.create_object_list(objs=frame_objs)

    # Copy the frame by vector
    rstab_app.move_objects(
        objects=frame_objs,
        create_copy=True,
        number_of_steps=FRAME_COUNT-1,
        direction_through=rstab.manipulation.DIRECTION_THROUGH_DISPLACEMENT_VECTOR,
        displacement_vector=common.Vector3d(x=0.0, y=FRAME_SPACING, z=0.0),
        spacing=FRAME_SPACING
    )

    # Build purlins
    purlin_objs = build_purlins()
    rstab_app.create_object_list(objs=purlin_objs)

    # Copy the purlins parallel to axis
    rstab_app.move_objects(
        objects=purlin_objs,
        create_copy=True,
        number_of_steps=FRAME_COUNT-2,
        direction_through=rstab.manipulation.DIRECTION_THROUGH_PARALLEL_TO_AXIS,
        axis=rstab.manipulation.COORDINATE_AXIS_Y,
        spacing=FRAME_SPACING
    )