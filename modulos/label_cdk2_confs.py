import pytraj as pt
import numpy as np


def get_distance_ij(traj_obj, atom_mask_i, atom_mask_j, distance = 5.0):
    '''
    Get the euclidean distance between two i and j atoms along a trajectory.
    Example: (traj, ':33@NZ :51@CD')
    '''
    distances = pt.distance(traj_obj, 'atom_mask_i atom_mask_j')
    return distances

def get_phi_angle(traj_obj, residue):
    ''' Evaluates the angle of a dihedral given a Trajectory object and a residue number'''
    phi = pt.calc_phi(traj_obj, resrange = residue)
    # phi.values is an array of n times n_frames
    return phi

def get_geom_center_distance(traj_obj, resmask_1, resmask_2):
    ''' Evaluates the distance between the geometry center of two sets of atoms 
    given a Trajectory object and two Amber atoms mask'''
    center_1 = pt.calc_center_of_geometry(traj_obj, resmask_1)
    center_2 = pt.calc_center_of_geometry(traj_obj, resmask_2)
    center_distance = np.linalg.norm( center_1 - center_2, axis = 1)
    return center_distance

def secondary_struc(traj_obj, residues_mask):
    ''' Returns the secondary structure string of a given subsecuence 
    and a Trajectory object'''
    dssp_traj = pt.dssp_analysis.dssp(traj_obj,
        residues_mask)
    # dssp_traj[1] has n_frames, n_residues shape
    return dssp_traj[1]


def label_cdk2_conformations(traj_obj, 
    saltbridge_cutoff = 5.0,
    dfg_angle_cutoff = 0.0,
    center_dist_cutoff = 14.5,
    min_num_res_helix = 4):

    # Evaluates if the LYS-GLU salt bridge exists
    att_1 = get_distance_ij(traj_obj, ':33@NZ', ':51@CD')
    is_salt_bridge = att_1 < saltbridge_cutoff

    # Evaluates if the structure is DFG-OUT
    att_2 = get_phi_angle(traj_obj, '145')
    is_dfg_out = att_2 < dfg_angle_cutoff

    # Evaluates if the structure is Open
    aC_b4_distances = get_geom_center_distance(traj_obj, ':46-55', ':78-81')
    is_open = aC_b4_distances > center_dist_cutoff

    # Evaluates if the A-loop has a secondary structure (helix)
    sec_struc = secondary_struc(traj_obj, ':146-156')
    is_helix = np.char.count(sec_struc, 'H').sum(axis=1) >= min_num_res_helix

