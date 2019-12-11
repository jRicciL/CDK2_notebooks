from modules.MDS import cMDS_proj
from sklearn.decomposition import PCA

def process_pca(traj, ref = 0,  n_vecs = 2):
    '''
    Performs PCA over a given trajectory
    Parameters:
        traj (pytraj.Trajectory): pytraj Trajectory object with sliced atoms
        ref (int): number of conformation inside traj to use as reference to superpose traj
        n_vects (int): Number of pca eigenvectors to return
    Returns:
        dict_pca: dictionary with
            pca (numpy array): n_vects eigenvectors
            variance (numpy array): explained variance of the n_vects eigenvectors
    '''
    # Copia el objeto traj a uno nuevo, pero sólo los átomos de mask
    traj_temp = traj.copy()
    traj_temp.superpose(ref = 0) # Superpone usando la  referencia indicada
    # Crea la matriz 2d de coordenadas por frame
    xyz_2d = traj_temp.xyz.reshape(traj_temp.n_frames, traj_temp.n_atoms * 3)
    # Realiza el PCA
    pca = PCA(n_components = n_vecs)
    components = pca.fit_transform(xyz_2d)
    dict_pca = {'pca': components, 'variance': pca.explained_variance_ratio_ * 100}
    return(dict_pca)
    
def get_sup_points_projected_mds(MDS_ref_object, traj_reference, 
                                 traj_out_of_sample, ref = 0, n_components = 2):
    '''
    Obtain the D-suplementary RMSD matrix of a suplementary trajectory and 
    perfroms cMDS projection of out of sample points by using get_sup_rmsd_pairwise() function.
    
    Parameters:
        MDS_ref_object (MDS object): cMDS object.
        traj_reference (pytraj.trajectory): pytraj Trajectory object with m frames and sliced atoms
        traj_out_of_sample: pytraj Trajectory object with n frames sliced atoms
        ref (int):  number of conformation inside traj_reference to use 
                    as reference to superpose traj_out_of_sample
        n_vects (int): Number of mds eigenvectors to return
    Returs:
        mds_projected (numpy narray): n_vects mds eigenvectors
    '''
    # Se generan copias temporales de los objetos
    full_traj = traj_reference.copy()
    sup_traj = traj_out_of_sample.copy()
    # Se obtiene el número de frames de cada trayectoria
    m_ref_frames = full_traj.n_frames
    n_sup_frames = sup_traj.n_frames
    # Ahora generamos una única trayectoria uniendo la referencia con la suplementaria
    full_traj.append_xyz(sup_traj.xyz)
    # Y superponemos al primer frame de referencia
    full_traj.superpose(ref = ref)
    # Ahora full_traj tiene m+n frames
    m_plus_n_frames = full_traj.n_frames
    # Se genera la matriz suplementaria m conf referencia por n confs suplementarias
    mtx_rmsd_sup = np.empty((m_ref_frames, n_sup_frames))
    
    for i in range(m_ref_frames):
        # Se calcula el RMSD de cada frame i de la traj de referencia vs la traj suplementaria
        rmsd = pyt.rmsd(traj= full_traj, ref = i, 
                        nofit=True, 
                        # Sólo calcula el rmsd para los sup_frames
                        frame_indices = range(m_ref_frames, m_plus_n_frames))
        mtx_rmsd_sup[i] = rmsd
    # m * n matrix with RMSD values of  traj_out_of_sample frames againts traj_reference frames.
    # Performs th projection
    mds_projected = cMDS_proj(MDS_ref_object, mtx_rmsd_sup.T)
    
    return( mds_projected[: , 0 : n_components].T )