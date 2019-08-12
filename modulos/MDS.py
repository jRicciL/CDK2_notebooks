import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mpltcols
import matplotlib.patches as mpatches

def cMDS(D):
    # Modificado de: http://www.nervouscomputer.com/hfs/cmdscale-in-python/
    # Número de observaciones                                                                
    n = len(D)
    # Se genera la matriz de distancia al cuadrado (Squared proximity matrix)
    D_sq = D**2
    # Se genera la matriz de  centrado J (Centering matrix)
    # Definida como la matriz de identidad In menos la matriz de nxn unos/n
    e1 = np.ones((n,1))
    m = ( np.ones((n, 1)) / n)
    I = np.eye(n) # Matriz de identidad I_n
    J = I - e1.dot(np.transpose(m)) # Matriz de centrado
    # Se genera la matriz B, definida como B = -0.5*J*D^2*J                                                                                 
    B = -(1/2) * J.dot(D_sq).dot(J) # como J es simétrica da lo mismo teansponerla o no

    # Se determinan los eigenvalores y eigenvectores de la matriz B                                                                         
    e_vals, e_vecs = np.linalg.eigh(B)

    # Se ordenan los eigenvalores de mayor a menor
    idx   = np.argsort(e_vals)[::-1] # Se extraen los índices de ordenamiento
    e_vals = e_vals[idx] # Se ordena cada vector según el eigenvalor
    e_vecs = e_vecs[:,idx]
    w, = np.where(e_vals > 0) # Se seleccionan los índices donde los eValores son positivos
    e_vals = e_vals[w]
    # Se obtiene la matriz de configuración F = M^(-1/2)*E_m*L_m^(1/2)  
    M_neg_sq = np.diag(m[:,0]**(-0.5)) # M_neg_sq es la matriz M^(-1/2)
    L_m_sq  = np.diag(np.sqrt(e_vals[w])) #  Lambda_sq (L_m^(1/2)) es la matriz diagonal con la raiz cuadrada de m eigenValores positivos
    E_m = e_vecs[:,w] # E_m  es la matriz con los m eigenvectores positivos y ordenados
    # F  = M_neg_sq.dot(E_m.dot((L_m_sq)))  # F = M^(-1/2)*E_m*L_m^(1/2)
    F = E_m.dot((L_m_sq))
    #print(B == (X.transpose()).dot(X) )

    return F.T, D_sq, B, e_vals

def cMDS_proj(cMDS_obj, sup_point):
    # Recibe un objeto cMDS_obj
    F = cMDS_obj[0].T # Matriz F de scores obtenida con cMDS a partir de los valores "Activos"
    D_sq = cMDS_obj[1] # Matrix Delta^2
    e_vals = cMDS_obj[3] # Eigenvalores positivos obtenidos del B de los valores "Activos"
    n = len(D_sq)
    e1 = np.ones((n, 1))
    m = len(sup_point)
    e1_sup = np.ones((m, 1))
    m = ( np.ones((n, 1)) / n)
    I = np.eye(n) # Matriz de identidad I_n
    J = I - e1.dot(np.transpose(m)) # Mariz de centrado
    # MDS out-of-smaple: Adición de un punto suplementario
    a_out = sup_point**2
    # D_sup_2 es un vector con los valores de RMSD del nuevo punto frente a los "Activos"
    # Se calcula B_sup como -0.5*J*(a_out - D^2*(m1^t))
    B_sup = -0.5 * J.dot(a_out.T - D_sq.dot(m.dot(np.transpose(e1_sup))))
    # Finalmente se calcula F_sup = (B_sup^t)*F*L_inv
    # Donde L_inv es la matriz diagonal con la inversa de los eingenvalores
    L_m_inv = np.diag( 1 / e_vals )
    F_proj = np.transpose(B_sup).dot( F ).dot( L_m_inv)
    return F_proj


def plot_mds_or_pca(mds, labels = None,
    colors_list = ['red', 'cyan', 'green', 'blue', 'orange', 'gray'],
    dic_of_ref_labels = None,
    traj_labels = None,
    alpha=0.6, fig_size = 7, refs_fontsize = 15,
    point_size = 60,
    title = "Classic MDS",
    xlabel = "Primer componente",
    ylabel = "Segundo componente",
    legend = False,
    equal_axis = True,
    xy_lims = None):

    # Properties of the scatter plot
    colors = colors_list
    plt.rcParams.update({'font.size': 16})
    plt.axhline(0, color='grey',  linestyle='--')
    plt.axvline(0, color='grey',  linestyle='--')
    plt.title(title, fontsize=18)
    plt.xlabel(xlabel, fontsize = 14)
    plt.ylabel(ylabel, fontsize = 14)


    if labels is not None:
        # Color by label
        name_labels =  list(np.unique( labels ))
        if len(colors_list) < len(name_labels):
                print(F'El número de colores en la lista ({len(colors_list)}) es menor al número único de etiquetas ({len(name_labels)}).')
                return None
        color_numeric_labels = range(len(name_labels))
        code_labels = dict(zip(name_labels, colors_list[:len(name_labels)]))
        color_labels = [ code_labels[i] for i in labels]
        
        for label in code_labels:
            if label != 'None':
                indices = np.where(label == labels)
                plt.scatter( mds[0][indices], mds[1][indices], marker='o', c = code_labels[label],  alpha=alpha, s= point_size)
        
        # plt.scatter( mds[0], mds[1], marker='o', c = color_labels,  alpha=alpha, s=60)
        
        if legend:
            patchList = []
            for key in code_labels:
                data_key = mpatches.Patch(color = code_labels[key], label=key)
                patchList.append(data_key)
            plt.legend(handles=patchList)
        
    else:
        plt.scatter( mds[0], mds[1], marker='o', c = colors_list[0], alpha=alpha, s=60)

    if dic_of_ref_labels is not None  and  traj_labels is not None:
        # Creates the refs label and its color
        name_ref_label, color_ref_label = zip(*[(i, dic_of_ref_labels[i])  if i in dic_of_ref_labels.keys() else ("None", "None") for i in traj_labels])
        # plots the labels of the given references indixes 
        for label, x, y in zip( name_ref_label, mds[0], mds[1]):
            if label != 'None':
                plt.scatter(x, y, marker='o', s=80, c = "None", linewidths = 1.5, edgecolors = "black")
                plt.annotate(label.split("_")[0], xy = (x, y), fontsize = refs_fontsize, weight = 'bold')
    if xy_lims is not None and len(xy_lims) == 4:
        plt.xlim(xy_lims[0], xy_lims[1])
        plt.ylim(xy_lims[2], xy_lims[3])
    if equal_axis:
        plt.axis('equal')
    plt.grid(linestyle='--')