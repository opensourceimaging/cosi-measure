import numpy as np

def get_magnet_center_abs(pos_right_screw:np.array, pos_left_screw:np.array, pos_top_screw:np.array, probe_distance_from_tip = 2.05):
    '''
    calculates the center position of osi2-one magnet from 3 ref points aka ref screws. Everything in COSI coordinates


    # Args:

    - pos_right_screw:np.array. Position of the right screw in mm x,y,z

    - pos_left_screw:np.array. Position of the left screw in mm x,y,z

    - pos_top_screw:np.array. Position of the top screw in mm x,y,z

    - probe_distance_from_tip:float. Optional. This defines the offset from the mechanical center tip of the probe to the magnetic center. Default: 2.05.

    # Returns:

    - x,y,z in Cosi coordinates. Center position.

    '''
    probe_distance_from_tip = 2.05 # in -y of Cosi
    magnet_bore_half_length = 240+9 # +9 is offset from stuff in front, e.g. screws. 

    center_in_xz_plane_magnet_front = (pos_right_screw+pos_left_screw)/2

    vector_frontplaneCenter_2_top = pos_top_screw - center_in_xz_plane_magnet_front

    vector_fronplaneCenter_left_right = pos_right_screw - pos_left_screw

    #magnet_y_direction = np.cross(vector_fronplaneCenter_left_right, vector_frontplaneCenter_2_top)

    vector_frontplaneCenter_2_right = pos_right_screw - center_in_xz_plane_magnet_front

    magnet_y_direction = np.cross(vector_frontplaneCenter_2_top, vector_frontplaneCenter_2_right) + center_in_xz_plane_magnet_front

    magnet_y_direction_normalized = magnet_y_direction/np.linalg.norm(magnet_y_direction)

    centerpoint = center_in_xz_plane_magnet_front + magnet_y_direction_normalized * (magnet_bore_half_length + probe_distance_from_tip)

    return centerpoint

