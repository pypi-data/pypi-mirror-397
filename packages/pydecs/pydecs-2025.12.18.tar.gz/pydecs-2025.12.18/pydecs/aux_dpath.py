import sys,os,csv,copy,toml,glob,argparse,math
from termios import NL1
from shutil import copyfile
import shutil
import numpy as np
from itertools import product
from collections import OrderedDict
from scipy.spatial import cKDTree as KDTree
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from pydecs.aux_prep import check_duplication

def parse_poscar_dpath(path):
    with open(path) as f:
        L = [l.strip() for l in f if l.strip()]
    scale = float(L[1].split()[0])
    lattice = np.array([[float(x) for x in L[i].split()] for i in (2,3,4)]) * scale
    elems  = L[5].split()
    counts = [int(x) for x in L[6].split()]
    coord_type = L[7][0].upper()  # 'C' or 'D' など
    type_grouped = any("[" in el for el in elems)

    coords = []
    symbols = []
    idx = 8
    for el, cnt in zip(elems, counts):
        for _ in range(cnt):
            frac = [float(x) for x in L[idx].split()[:3]]
            idx += 1
            coords.append(frac)
            symbols.append(el)
    coords = np.array(coords)
    return lattice, coords, symbols, type_grouped

def trim_group_parenthesis(symbol):
    if "[" in symbol:
        return symbol.split("[")[0]
    else:
        return symbol


def output_vasp(fn_outvasp, structure, coords_are_cartesian=False):
    with open(fn_outvasp, "w") as f:
        f.write("pathPristine\n1.0\n")
        for v in structure["cell"]:
            f.write(f"{v[0]:.10f} {v[1]:.10f} {v[2]:.10f}\n")
        elems = structure["elements"]
        coords = structure["coords"]
        elems_list = []
        elems_list_trim = []
        for e1 in elems:
            #if e1 == "Fr" or "Rn" in e1:
            if e1 == "Fr":
                continue
            if e1 not in elems_list:
                elems_list.append(e1)
            e2 = trim_group_parenthesis(e1)
            if e2 not in elems_list_trim:
                elems_list_trim.append(e2)
        elems_list.append("Fr")
        elems_list_trim.append("Fr")
        coords_dict = {}
        for e1 in elems_list:
            coords_dict[e1] = []
        for e1,c1 in zip(elems,coords):
            if e1 in elems_list:
                coords_dict[e1].append(c1)
        num_elems_list_trim = {}
        for e1 in elems_list:
            e2 = trim_group_parenthesis(e1)
            if e2 not in num_elems_list_trim:
                num_elems_list_trim[e2] = 0
            num_elems_list_trim[e2] += len(coords_dict[e1])
        for e1 in elems_list_trim:
            if num_elems_list_trim[e1] > 0:
                f.write(f"{e1} ")
        f.write("\n")
        for e1 in elems_list_trim:
            if num_elems_list_trim[e1] > 0:
                f.write(f"{num_elems_list_trim[e1]} ")
        f.write("\n")
        if coords_are_cartesian:
            f.write("Cartesian\n")
        else:
            f.write("Direct\n")
        for e1 in elems_list:
            for c in coords_dict[e1]:
                f.write(f"{c[0]:.10f} {c[1]:.10f} {c[2]:.10f}\n")
    return

def search_diffpath_long():
    default_toml = """
#### Common
input_POSCAR = "***.vasp"
# clean_dpath = true
# centering_wrt_initial_site = true
# cutoffR_naigh = 5.0
# chkdupl_tolerance = 0.0001
# network_elements = ["O","Rn"]
# max_path_length = 4
# k_path = 10
# bvse_calc = false
# bvse_mobile_ion = "Li1+"
# bvse_mesh_resolution = 0.1
# bvse_mesh_rcut = 10.0
# bvse_mesh_k = 100
# bvse_singleHop_delx = 0.1
# bvse_singleHop_Rmax = 0.1
# bvse_singleHop_delR = 0.05
# bvse_singleHop_angle = 10
# bvse_plot_singleHopping = true

#### Long-range path-network searth
# long_diff_atom_sites = [5,7] # ["F[1]","F[2]"] # ["Rn"]
# long_search_image_range = 1   #  [[1,0,0],[0,0,1]]

#### Specific-pair path-network search
# pair_atom_ids = [[4,4],[5,7]] ## List of pair of atom IDs
# pair_image_cell_positions = [[1,0,0],[0,0,0]]  ## Default: List of [0,0,0]
    """
    print("  Starting pydecs-dpath-long tool.")
    try:
        import networkx as nx
    except ImportError:
        raise ImportError("The 'networkx' library is not installed. Please install it with 'pip install networkx'.")

    try:
        from bvlain import Lain
    except ImportError:
        raise ImportError("The 'bvlain' library is not installed. Please install it with 'pip install bvlain'.")
    try:
        from pymatgen.core import Lattice,Structure 
        from pymatgen.io.common import VolumetricData
    except ImportError:
        raise ImportError("The 'pymatgen' library is not installed. Please install it with 'pip install pymatgen'.")
    parser = argparse.ArgumentParser(description="pydecs-dpath-long tool")
    parser.add_argument("-p", action="store_true", help="Create a template configuration file")
    args = parser.parse_args()
    if args.p:
        fname = "inpydecs_dpath_long.toml"
        if os.path.exists(fname):
            print(f"  {fname} already exists.")
            print("  The template is as follows:")
            print("#"*50)
            print(default_toml.strip())
            print("#"*50)
        else:
            print(f"  Creating {fname}.")
            with open(fname, "w") as f:
                f.write(default_toml.strip() + "\n")
            print(f"  {fname} has been created.")
        sys.exit()

    # Setting input parameters
    print("  Reading input file: inpydecs_dpath_long.toml")
    if not os.path.exists('inpydecs_dpath_long.toml'):
        print("  Error!! inpydecs_dpath_long.toml not found.")
        print("  Please create the file with -p option.")
        print("  $ pydecs-dpath-long -p")
        sys.exit()
    with open('inpydecs_dpath_long.toml', 'r') as f:
        config = toml.load(f)
    if 'input_POSCAR' not in config:
        raise KeyError("The 'input_POSCAR' tag is required in the configuration file.")
    input_POSCAR = config['input_POSCAR']
    clean_dpath = False
    if 'clean_dpath' in config:
        clean_dpath = config['clean_dpath']
    supercell_size = [0,0,0]
    if 'supercell_size' in config:
        supercell_size = config['supercell_size']
        if isinstance(supercell_size, int):
            supercell_size = [supercell_size, supercell_size, supercell_size]
        elif isinstance(supercell_size, (list, tuple)) and len(supercell_size) == 3 and all(isinstance(x, int) for x in supercell_size):
            pass
        else:
            raise ValueError("supercell_size must be specified as an integer or a list of three integers.")
    else:
        print("  Error!! supercell_size is not set. Please set it in the configuration file.")
        sys.exit()
    centering_wrt_initial_site = False
    if 'centering_wrt_initial_site' in config:
        centering_wrt_initial_site = config['centering_wrt_initial_site']
    cutoffR_naigh = 5.0
    if 'cutoffR_naigh' in config:
        cutoffR_naigh = config['cutoffR_naigh']
    k_path = 10
    if 'k_path' in config:
        k_path = config['k_path']
    max_path_length = 4
    if 'max_path_length' in config:
        max_path_length = config['max_path_length']
    chkdupl_tolerance = 0.0001
    if 'chkdupl_tolerance' in config:
        chkdupl_tolerance = config['chkdupl_tolerance']
    network_elements = None
    if 'network_elements' in config:
        network_elements = config['network_elements']
    bvse_mobile_ion = None
    if 'bvse_mobile_ion' in config:
        bvse_mobile_ion = config['bvse_mobile_ion']
    bvse_calc = False
    if bvse_mobile_ion is not None:
        bvse_calc = True
    if 'bvse_calc' in config:
        bvse_calc = config['bvse_calc']
    if bvse_calc:
        if bvse_mobile_ion is None:
            print("  Error!! bvse_mobile_ion is not set. Please set it in the configuration file.")
            sys.exit()
    bvse_mesh_resolution = 0.1
    if 'bvse_mesh_resolution' in config:
        bvse_mesh_resolution = config['bvse_mesh_resolution']
    bvse_mesh_rcut = 10.0
    if 'bvse_mesh_rcut' in config:
        bvse_mesh_rcut = config['bvse_mesh_rcut']
    bvse_mesh_k = 100
    if 'bvse_mesh_k' in config:
        bvse_mesh_k = config['bvse_mesh_k']
    bvse_singleHop_delx = 0.1
    if 'bvse_singleHop_delx' in config:
        bvse_singleHop_delx = config['bvse_singleHop_delx']
    bvse_singleHop_delR = 0.05
    if 'bvse_singleHop_delR' in config:
        bvse_singleHop_delR = config['bvse_singleHop_delR']
    bvse_singleHop_Rmax = 0.1
    if 'bvse_singleHop_Rmax' in config:
        bvse_singleHop_Rmax = config['bvse_singleHop_Rmax']
    bvse_singleHop_delR = 0.05
    if 'bvse_singleHop_delR' in config:
        bvse_singleHop_delR = config['bvse_singleHop_delR']
    bvse_singleHop_angle = 10
    if 'bvse_singleHop_angle' in config:
        bvse_singleHop_angle = config['bvse_singleHop_angle']
    bvse_plot_singleHopping = False
    if 'bvse_plot_singleHopping' in config:
        bvse_plot_singleHopping = config['bvse_plot_singleHopping']
    long_diff_atom_sites = None
    if 'long_diff_atom_sites' in config:
        long_diff_atom_sites = config['long_diff_atom_sites']
    long_search_image_range = 1
    if 'long_search_image_range' in config:
        long_search_image_range = config['long_search_image_range']
        if isinstance(long_search_image_range, int):
            pass
        elif (isinstance(long_search_image_range, (list, tuple)) and
              all(isinstance(x, (list, tuple)) and len(x) == 3 and all(isinstance(xx, int) for xx in x) for x in long_search_image_range)):
            long_search_image_range = [list(x) for x in long_search_image_range]
        else:
            raise ValueError("long_search_image_range must be specified as an integer or a list of 3-element lists/tuples of integers (e.g., [[0,0,1],[1,0,0]]).")
    pair_atom_ids = None
    if 'pair_atom_ids' in config:
        pair_atom_ids = config['pair_atom_ids']
    pair_image_cell_positions = []
    if 'pair_image_cell_positions' in config:
        pair_image_cell_positions = config['pair_image_cell_positions']
    if pair_atom_ids is not None:
        if len(pair_atom_ids) != len(pair_image_cell_positions):
            raise ValueError("The number of pair_atom_ids and pair_image_cell_positions must be the same.")
        for idx, pair in enumerate(pair_atom_ids):
            if not (isinstance(pair, (list, tuple)) and len(pair) == 2 and all(isinstance(x, int) for x in pair)):
                raise ValueError(f"Each element of pair_atom_ids must be a list or tuple of two integers. Error at index {idx}: {pair}")
        for idx, cell in enumerate(pair_image_cell_positions):
            if not (isinstance(cell, (list, tuple)) and len(cell) == 3 and all(isinstance(x, int) for x in cell)):
                raise ValueError(f"Each element of pair_image_cell_positions must be a list or tuple of three integers. Error at index {idx}: {cell}")

    print("    input poscar: ", input_POSCAR)
    print("    clean_dpath: ", clean_dpath)
    print("    supercell_size: ", supercell_size)
    print("    centering_wrt_initial_site: ", centering_wrt_initial_site)
    print("    cutoffR_naigh: ", cutoffR_naigh)
    print("    k_path: ", k_path)
    print("    max_path_length: ", max_path_length)
    print("    chkdupl_tolerance: ", chkdupl_tolerance)
    if network_elements is not None:
        print("    network_elements: ", network_elements)
    else:
        print("    network_elements: on-the-same-element-lattice")
    if bvse_calc:
        print("    bvse_mobile_ion: ", bvse_mobile_ion)
        print("    bvse_mesh_resolution: ", bvse_mesh_resolution)
        print("    bvse_mesh_rcut: ", bvse_mesh_rcut)
        print("    bvse_mesh_k: ", bvse_mesh_k)
        print("    bvse_singleHop_delx: ", bvse_singleHop_delx)
        print("    bvse_singleHop_Rmax: ", bvse_singleHop_Rmax)
        print("    bvse_singleHop_delR: ", bvse_singleHop_delR)
        print("    bvse_singleHop_angle: ", bvse_singleHop_angle)
        print("    bvse_plot_singleHopping: ", bvse_plot_singleHopping)
    else:
        print("    bvse_calc: False")
    print("    long_diff_atom_sites: ", long_diff_atom_sites)
    print("    long_search_image_range: ", long_search_image_range)
    print("    pair_atom_ids: ", pair_atom_ids)
    print("    pair_image_cell_positions: ", pair_image_cell_positions)
    print("  "+"-"*50)
    if clean_dpath:
        print("  Cleaning the dpath folders")
        os.system("rm -rf dpath*")
        print("  "+"-"*50)

    ### Reading input POSCAR ###
    print(f"  Reading input POSCAR: {input_POSCAR}")
    latt_const, coords, symbols, type_grouped = parse_poscar_dpath(input_POSCAR)
    symbol_counts = OrderedDict()
    for s in symbols:
        if s in symbol_counts:
            symbol_counts[s] += 1
        else:
            symbol_counts[s] = 1
    num_sites = list(symbol_counts.values())
    num_sites_tot = sum(num_sites)
    symbols_list = list(dict.fromkeys(symbols))
    symbols_trim = [trim_group_parenthesis(s) for s in symbols]
    elems_counts = OrderedDict()
    for s in symbols_trim:
        if s in elems_counts:
            elems_counts[s] += 1
        else:
            elems_counts[s] = 1
    num_elems = list(elems_counts.values())
    num_elems_tot = sum(num_elems)
    elems_list = list(dict.fromkeys(symbols_trim))
    print("    site list: ", symbols_list)
    print("    num_sites: ", num_sites)
    print("    elements: ", elems_list)
    print("    num_elems: ", num_elems)
    print("  "+"-"*50)

    ### check and set long_diff_atom_indexes ###
    long_diff_atom_indexes = []
    if long_diff_atom_sites is not None:
        if isinstance(long_diff_atom_sites, list):
            if all(isinstance(x, int) for x in long_diff_atom_sites):
                pass
            elif all(isinstance(x, str) for x in long_diff_atom_sites):
                for x in long_diff_atom_sites:
                    if type_grouped:
                        if not (x in elems_list or x in symbols_list):
                            print(f"  Error!! Each element in long_diff_atom_sites must be a site-symbol or element name.\n   {x} is not found in symbols_list={symbols_list} or elements={elems_list}")
                            sys.exit()
                    else:
                        if not (x in elems_list):
                            print(f"  Error!! Each element in long_diff_atom_sites must be a site-symbol or element name.\n   {x} is not found in elements={elems_list}")
                            sys.exit()
            else:
                print("  Error!! long_diff_atom_sites must be a list of integers or a list of strings.")
                sys.exit()
        else:
            print("  Error!! long_diff_atom_sites must be a list of integers or a list of strings.")
            sys.exit()
    print("  "+"-"*80)

    ### set id and image-cell directions for diffusion-path search ###    
    print("  Setting pair-lists")
    if long_diff_atom_sites is None and pair_atom_ids is None:
        print("  Error!! Either long_diff_atom_sites or pair_atom_ids/pair_image_cell_positions must be set. Please set one of them.")
        sys.exit()
    print("    pair_list_long:")
    imcell_list = []
    if long_diff_atom_sites is not None:
        if isinstance(long_search_image_range, int):
            max_image_cells = abs(long_search_image_range)
            imcell_list = list(product(range(-max_image_cells,max_image_cells+1), repeat=3))
        else:
            imcell_list = long_search_image_range
    pair_list_long = []
    id_pair_all = 1
    if long_diff_atom_sites is not None:
        for da1 in long_diff_atom_sites:
            id_target = da1
            if isinstance(da1, str):
                id_target_candidates = []
                if da1 in symbols:
                    id_target_candidates = [i+1 for i, s in enumerate(symbols) if s == da1]
                else:
                    id_target_candidates = [i+1 for i, s in enumerate(symbols_trim) if s == da1]
                if len(id_target_candidates) == 0:
                    print(f"  Error!! No candidates found for symbol {da1}")
                    sys.exit()
                id_target = id_target_candidates[0]
            else:
                if id_target > len(symbols):
                    print(f"  Error!! id_target={id_target} from long_diff_atom_sites is out of range. Please check the input file.")
                    sys.exit()
            elem_target = symbols[id_target-1]
            for tx,ty,tz in imcell_list:
                if tx==0 and ty==0 and tz==0:
                    continue
                pair = {
                    "start_id": id_target,
                    "start_elem": elem_target,
                    "end_id": id_target,
                    "end_elem": elem_target,
                    "image_cell": (tx,ty,tz)
                }
                if pair not in pair_list_long:
                    pair["id"] = f"{id_pair_all:04d}"
                    fn_outvasp = f"dpathPristine_{pair['id']}.vasp"
                    pair["filename"] = fn_outvasp
                    pair_list_long.append(pair)
                    id_pair_all += 1
                else:
                    print(f"      Warning!! The path ({pair['start_id']}({pair['start_elem']}) in (0,0,0) to {pair['end_id']}({pair['end_elem']}) in {pair['image_cell']}) is skipped because it is already in the list.")
    if pair_list_long:
        for i, pair in enumerate(pair_list_long):
            print(f"      Path-{pair['id']}: From {pair['start_id']}({pair['start_elem']}) in (0,0,0) to {pair['end_id']}({pair['end_elem']}) in {pair['image_cell']}")
    else:
        print("        (nothing)")
    pair_list_all = copy.deepcopy(pair_list_long)
    print("    pair_list_specific_pairs:")
    pair_list_pair = []
    if pair_atom_ids is not None:
        for ip1, p1 in enumerate(pair_atom_ids):
            cell = pair_image_cell_positions[ip1]
            if p1[0]==p1[1] and cell==[0,0,0]:
                continue
            pair = {
                "start_id": p1[0],
                "start_elem": symbols[p1[0]-1],
                "end_id": p1[1],
                "end_elem": symbols[p1[1]-1],
                "image_cell": tuple(cell)
            }
            if pair not in pair_list_all:
                pair["id"] = f"{id_pair_all:04d}"
                fn_outvasp = f"dpathPristine_{pair['id']}.vasp"
                pair["filename"] = fn_outvasp
                pair_list_pair.append(pair)
                pair_list_all.append(pair)
                id_pair_all += 1
            else:
                print(f"      Warning!! The path ({pair['start_id']}({pair['start_elem']}) in (0,0,0) to {pair['end_id']}({pair['end_elem']}) in {pair['image_cell']}) is skipped because it is already in the list.")
    if pair_list_pair:
        for i, pair in enumerate(pair_list_pair):
            print(f"      Path-{pair['id']}: From {pair['start_id']}[{pair['start_elem']}) in (0,0,0) to {pair['end_id']}({pair['end_elem']}) in {pair['image_cell']}")
    else:
        print("        (nothing)")
    print("  "+"-"*50)
    if network_elements is not None:
        print("  Checking network_elements")
        for pair in pair_list_all:
            if trim_group_parenthesis(pair["start_elem"]) not in network_elements:
                print(f"  Error!! The start element of the path ({pair['start_elem']}) is not in network_elements.")
                print(f"    network_elements: {network_elements}")
                print(f"    Please check the input file.")
                sys.exit()
            if trim_group_parenthesis(pair["end_elem"]) not in network_elements:
                print(f"  Error!! The end element of the path ({pair['end_elem']}) is not in network_elements.")
                print(f"    network_elements: {network_elements}")
                print(f"    Please check the input file.")
                sys.exit()
        print("  "+"-"*50)

    ### Making the supercell structure ###
    print("  Making supercell structure and preparing network-structure nodes")
    nodes_all = []
    latt_const_supercell = latt_const * np.array(supercell_size)
    coords_supercell = []
    symbols_supercell = []
    idatom_supercell = 1
    if supercell_size == [1,1,1]:
        for ip1 in range(num_sites_tot):
            coords_supercell.append(coords[ip1])
            symbols_supercell.append(symbols[ip1])
            nodes_all.append({
                "atom-id":     idatom_supercell,
                "element": symbols[ip1],
                "coords":  coords[ip1]
            })
            idatom_supercell += 1
    else:
        for ip1 in range(num_sites_tot):
            for ic1, ic2, ic3 in product(range(supercell_size[0]), range(supercell_size[1]), range(supercell_size[2])):
                e1 = symbols[ip1]
                coords_supercell_tmp = [(coords[ip1][0]+ic1)/float(supercell_size[0]), 
                                        (coords[ip1][1]+ic2)/float(supercell_size[1]), 
                                        (coords[ip1][2]+ic3)/float(supercell_size[2])]
                coords_supercell.append(coords_supercell_tmp)
                symbols_supercell.append(e1)
                nodes_all.append({
                    "atom-id": idatom_supercell,
                    "element": e1,
                    "coords":  coords_supercell_tmp
                })
                for ipair, pair in enumerate(pair_list_all):
                    imcell = list(copy.deepcopy(pair["image_cell"]))
                    for j1 in range(3):
                        if imcell[j1] < 0:
                            imcell[j1] += supercell_size[j1]
                        if imcell[j1] >= supercell_size[j1]:
                            print("  Error!! image_cell is out of range.")
                            print(f"    image_cell of {j1+1}-th direction ({imcell[j1]}) in pair-id {ipair+1:04d} should be in the range of [0, {supercell_size[j1]-1}] from the supercell_size parameter.")
                            print(f"    supercell_size: {supercell_size}")
                            sys.exit()
                    if [ic1,ic2,ic3] == [0, 0, 0] and pair["start_id"] == ip1+1:
                            pair_list_all[ipair]["start_id_supercell"] = idatom_supercell
                    if imcell == [ic1, ic2, ic3] and pair["end_id"] == ip1+1:
                            pair_list_all[ipair]["end_id_supercell"] = idatom_supercell
                            pair_list_all[ipair]["image_cell_supercell"] = (ic1, ic2, ic3)
                idatom_supercell += 1
    coords_supercell = np.array(coords_supercell)
    structure_supercell = {
        "cell": latt_const_supercell,
        "elements": symbols_supercell,
        "coords": coords_supercell
    }
    output_vasp("dpath_supercell.vasp", structure_supercell)
    print(f"  Saved supercell structure as 'dpath_supercell.vasp'") 
    print("    pair_list_all for supercell:")
    for i, pair in enumerate(pair_list_all):
        print(f"      Path-{pair['id']}: From {pair['start_id_supercell']}({pair['start_elem']}) in (0,0,0) to {pair['end_id_supercell']}({pair['end_elem']}) in {pair['image_cell_supercell']}")
    print("  "+"-"*50)

    ### Calculating BVSE distribution ###
    print(f"  Calculating BVSE distribution")
    symbols_woRn = []
    coords_woRn = []
    for i1 in range(len(symbols)):
        if "Rn" not in symbols[i1]:
            symbols_woRn.append(trim_group_parenthesis(symbols[i1]))
            coords_woRn.append(coords[i1])
    structure = Structure(lattice=Lattice(latt_const), species=symbols_woRn, coords=coords_woRn)
    calcBVSE = Lain(verbose=True)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stBVSE = calcBVSE.read_structure(st=structure)
        calcBVSE.bvse_distribution(mobile_ion=bvse_mobile_ion, r_cut=bvse_mesh_rcut, resolution=bvse_mesh_resolution, k=bvse_mesh_k)
    energies = calcBVSE.percolation_barriers(encut=2.0)
    for k1 in energies.keys():
        print(f'  {k1[-2:]} percolation barrier is {round(energies[k1], 4)} eV')
    calcBVSE.write_cube("dpath_BVSE_unitcell", task='bvse')
    vol_bvse = VolumetricData.from_cube("dpath_BVSE_unitcell.cube")
    struct_bvse = vol_bvse.structure.copy()
    struct_bvse.make_supercell(supercell_size)
    new_data = {}
    for label, grid in vol_bvse.data.items():     
        new_data[label] = np.tile(grid, supercell_size)
    vol_super = VolumetricData(structure=struct_bvse,data=new_data)
    vol_super.to_cube("dpath_BVSE_supercell.cube")
    bvse_val_min = vol_bvse.data["total"].min()
    print(f"  Minimum value of BVSE distribution: {bvse_val_min}")
    print("  "+"-"*50)

    print("  Preparing coordinates in the circle for BVSE-Ebarrier calculation")
    bvse_coords_in_circle = [[0.0,0.0]]
    r = bvse_singleHop_delR
    while r <= bvse_singleHop_Rmax:
        theta = 0.0
        while theta < 360.0:
            # bvse_coords_in_circle.append((r, theta))
            x = r * math.cos(theta*math.pi/180.0)
            y = r * math.sin(theta*math.pi/180.0)
            bvse_coords_in_circle.append([x, y])
            theta += bvse_singleHop_angle
        r += bvse_singleHop_delR
    print(f"    The number of bvse_coords_in_circle: {len(bvse_coords_in_circle)}")
    bvse_coords_array = np.array(bvse_coords_in_circle)
    x_coords = bvse_coords_array[:, 0]
    y_coords = bvse_coords_array[:, 1]    
    plt.figure(figsize=(10, 10))
    plt.scatter(x_coords, y_coords, c='blue', alpha=0.6, s=20)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.title('BVSE Coordinates in Circle Distribution')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.savefig('dpath_bvse_2DdistributionInCircle.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("    Saved 2D-distribution plot for BVSE: 'dpath_bvse_2DdistributionInCircle.png'")
    print("  "+"-"*50)
    
    ### Cheking duplication in pair_list_all
    print("  Cheking duplication in pair_list_all")
    outdir = "dpath0000_allpairs_chkDupl"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    os.chdir(outdir)
    csv_path = "out_dpathPristine.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["pair_id","filename", "start_id_in_unitcell", "start_elem", "end_id_in_unitcell", "end_elem", "end_image_cell", "start_id_in_supercell", "end_id_in_supercell"])
        for pair in pair_list_all:
            writer.writerow([
                pair["id"],
                pair["filename"],
                pair["start_id"],
                pair["start_elem"],
                pair["end_id"],
                pair["end_elem"],
                pair["image_cell"],
                pair["start_id_supercell"],
                pair["end_id_supercell"],
            ])
    for pair in pair_list_all:
        symbols_supercell_tmp = []
        coords_center = None
        for ip1 in range(len(coords_supercell)):
            iat1 = ip1 + 1
            e1 = symbols_supercell[ip1]
            c1 = coords_supercell[ip1]
            if iat1 == pair["start_id_supercell"]:
                e1 = "Fr"
                coords_center = [c1[0], c1[1], c1[2]]
            elif iat1 == pair["end_id_supercell"]:
                e1 = "Fr"
            symbols_supercell_tmp.append(e1)
        coords_supercell_tmp = np.array(coords_supercell)
        coords_center = np.array(coords_center)+0.5
        if centering_wrt_initial_site:
            print(f"    Adopting centering with respect to the initial site")
            print(f"      coords_center: {coords_center}")
            for ip1 in range(len(coords_supercell_tmp)):
                coords_supercell_tmp[ip1][0] -= coords_center[0]
                coords_supercell_tmp[ip1][1] -= coords_center[1]
                coords_supercell_tmp[ip1][2] -= coords_center[2]
        structure = {
            "cell": latt_const_supercell,
            "elements": symbols_supercell_tmp,
            "coords": coords_supercell_tmp
        }
        pair["structure"] = structure
        output_vasp(pair["filename"], structure)
    path3 = f"dpathPristine_*.vasp"
    sys.argv = [
            "pydecs-prep-chkDupl",
            "-t",str(chkdupl_tolerance),
            *glob.glob(path3),
            ]
    print(f"    Running duplication check")
    check_duplication()
    with open("out_duplication.csv", "r") as f:
        groups = [ t1.strip()for t1 in f.readline().split(",")]
        files = [ t1.strip()for t1 in f.readline().split(",")]
    pair_grouped = []
    for ig1,g1 in enumerate(groups):
        f1 = files[ig1]
        for pair1 in pair_list_all:
            if pair1["filename"] == f1:
                pair_grouped.append(copy.deepcopy(pair1))
                break
        outdir1 = f"dpath{ig1+1:04d}_network"
        outdir2 = os.path.join("../",outdir1)
        if not os.path.exists(outdir2):
            os.makedirs(outdir2)
        fnout = f"dpathGrouped_{ig1+1:04d}.vasp"
        path_outvasp = os.path.join(outdir2, fnout)
        print(f"  Copying {f1} to {path_outvasp}")
        copyfile(f1, path_outvasp)
        pair_grouped[-1]["filename"] = fnout
        pair_grouped[-1]["folder"] = outdir1
        pair_grouped[-1]["id"] = ig1+1
    os.chdir("..")

    ###  processing for each pair_grouped ###
    hopping_path_list = []
    for pair in pair_grouped:
        print(f"    chdir: {pair['folder']}")
        os.chdir(pair["folder"])
        lc2 = pair["structure"]["cell"]
        coords2 = pair["structure"]["coords"]
        symbols2 = pair["structure"]["elements"]
        symbols_list2 = list(dict.fromkeys(symbols2))
        symbols_list2 = [s for s in symbols_list2 if s != "Fr"] + ["Fr"]
        symbols_list2_trim = [trim_group_parenthesis(s) for s in symbols_list2]
        network_elements_local = []
        if network_elements is not None:
            network_elements_local = network_elements
        else:
            for e1 in symbols_list2:
                if e1 in pair["start_elem"] or e1 in pair["end_elem"]:
                    network_elements_local.append(trim_group_parenthesis(e1))
        if len(network_elements_local) == 0:
            print(f"  Error!! No network elements found in {pair['folder']}")
            sys.exit()
        print(f"      network_elements_local: {network_elements_local}")

        coords_supercell_network = []
        nodes_network = []
        for e1 in network_elements_local:
            for node1 in nodes_all:
                if e1 == trim_group_parenthesis(node1["element"]):
                    coords_supercell_network.append(node1["coords"])
                    nodes_network.append(node1)
        coords_supercell_network = np.array(coords_supercell_network)

        print("    Constructing network graph")
        tree0   = KDTree(coords_supercell_network)
        G = nx.Graph()
        for n in nodes_network:
            G.add_node(n["atom-id"], element=n["element"], coords=n["coords"])
        num_edges_list = []
        for i1, node1 in enumerate(nodes_network):
            atom_id1,coord1 = node1["atom-id"], node1["coords"]
            cand_neighbor = []
            num_edges_tmp = 0
            for i2, node2 in enumerate(nodes_network):
                if i2 == i1:
                    continue
                atom_id2,coord2 = node2["atom-id"], node2["coords"]
                disp = np.array(coord2) - np.array(coord1)
                for j1 in range(3):
                    if disp[j1] < -0.5:
                        disp[j1] += 1.0
                    if disp[j1] >= +0.5:
                        disp[j1] -= 1.0
                disp_cart = lc2 @ disp
                disp_cart_norm = np.linalg.norm(disp_cart)
                if disp_cart_norm <= cutoffR_naigh:
                    cand_neighbor.append((atom_id2, disp_cart_norm, disp_cart))
            cand_neighbor.sort(key=lambda x: x[1])
            if len(cand_neighbor) == 0:
                print(f"    Warning!! No candidates found for {atom_id1}")
                continue
            unit_vectors_seen = set()
            for atom_id2, dist, disp_cart in cand_neighbor:
                unit_vector = tuple(np.round(disp_cart/dist, 6))
                bool_seen = False
                for v1 in unit_vectors_seen:
                    d1 = np.array(unit_vector) - np.array(v1)
                    if np.linalg.norm(d1) < 0.00001:
                        bool_seen = True
                if not bool_seen:
                    unit_vectors_seen.add(unit_vector)
                    G.add_edge(atom_id1, atom_id2, distance=float(dist))
                    num_edges_tmp += 1
            num_edges_list.append(num_edges_tmp)
        print(f"    Total number of edges in the network graph: {G.number_of_edges()}")
        num_edges_list_set = set(num_edges_list)
        print(f"    Number of edges for each node:")
        for i1 in num_edges_list_set:
            print(f"      {i1} edges for {num_edges_list.count(i1)} nodes")
        pos = nx.spring_layout(G, k=0.1, iterations=100)
        nx.draw(G, with_labels=True,alpha=0.5,pos=pos,edge_color="blue",font_size=6)
        plt.savefig("out001_network_without_path.png")
        plt.close()
        print(f"    Saved network structure as 'out001_network_without_path.png'")
        print("  "+"-"*50)

        id_start = pair["start_id_supercell"]
        id_end   = pair["end_id_supercell"]
        if id_start not in G or id_end not in G:
            print(f"    Error!! {id_start} or {id_end} in the supercell is not in this network")
            sys.exit()
        print(f"    Finding shortest paths from {id_start} to {id_end} in the supercell network")

        all_paths = []
        for path in nx.all_simple_paths(G, id_start, id_end,cutoff=max_path_length):
            total_distance = 0
            for i in range(len(path) - 1):
                total_distance += G.edges[path[i], path[i+1]]["distance"]
            all_paths.append((copy.deepcopy(path), total_distance))
        all_paths.sort(key=lambda x: x[1])
        print(f"      Number of all found paths within the max_path_length({max_path_length}): {len(all_paths)}")
        paths_3k = all_paths[:3*k_path]
        fnout = f"out002_short_paths_upto_3xk.csv"
        print(f"      Output short paths up to {3*k_path} paths into {fnout}")
        fout = open(fnout, "w")
        fout.write(f"path,distance\n")
        paths_3k_str = []
        for path,dist in paths_3k:
            str1 = ""
            for i,atom_id3 in enumerate(path):
                str1 += f"{atom_id3}({symbols_supercell[atom_id3-1]})"
                if i < len(path)-1:
                    str1 += "-"
            paths_3k_str.append(str1)
            fout.write(f"{str1},{dist:.6f}\n")
        fout.close()
        paths_k = all_paths[:k_path]
        paths_k_str = paths_3k_str[:k_path]
        print(f"      Output short paths up to {k_path} paths")
        print(f"        distance | path")
        for (path,dist),path_str in zip(paths_k,paths_k_str):
            print(f"      {dist:10.6f} | {path_str}")

        folder_path = "out003_shortPaths upto_k"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        os.chdir(folder_path)
        fout = open("out_shortPaths.csv", "w")
        fout.write(f"id,distance,path\n")
        id_path = 1
        folder_path_k_list = []
        for (path,dist),path_str in zip(paths_k,paths_k_str):
            structure_mod = copy.deepcopy(pair["structure"])
            elements_mod = structure_mod["elements"]
            for atom_id3 in path:
                elements_mod[atom_id3-1] = "Fr"
            fn_outvasp = f"outPath_{id_path:04d}.vasp"
            output_vasp(fn_outvasp, structure_mod)
            print(f"      Writing supercell with path replaced by Fr: {fn_outvasp}")
            fout.write(f"{id_path:04d},{dist:.6f},{path_str}\n")
            folder_path_k_list.append(fn_outvasp)
            id_path += 1
        fout.close()
        path3 = f"outPath_*.vasp"
        sys.argv = [
                "pydecs-prep-chkDupl",
                "-t",str(chkdupl_tolerance),
                *glob.glob(path3),
                ]
        print(f"    Running duplication check") 
        check_duplication()
        with open("out_duplication.csv", "r") as f:
            groups = [ t1.strip()for t1 in f.readline().split(",")]
            files = [ t1.strip()for t1 in f.readline().split(",")]
        folder_path = "../out004_paths_candidates"
        print(f"    Extracting paths candidates within {folder_path}")
        if not os.path.exists(folder_path):
            print(f"      Making folder: {folder_path}")
            os.makedirs(folder_path)
        path_candidates = []
        dist_candidates = []
        path_candidates_str = []
        filename_candidates = []
        for ig1,g1 in enumerate(groups):
            f1 = files[ig1]
            f2 = f"outpathCand_{ig1+1:04d}.vasp"
            copyfile(f1, os.path.join(folder_path,f2))
            print(f"    Copying {f1} to {os.path.join(folder_path,f2)}")
            for (path1,dist1),f3,str1 in zip(paths_k,folder_path_k_list,paths_k_str):
                if f1 == f3:
                    path_candidates.append(path1)
                    dist_candidates.append(dist1)
                    path_candidates_str.append(str1)
                    filename_candidates.append(f2)

        fnout = os.path.join(folder_path, "out_singleHoppingPaths_all.csv")
        print(f"    Writing all single hopping paths into {fnout}")
        fout = open(fnout, "w")
        fout.write(f"path-id,filename,site1,site2,atom_id1,atom_id2,distance,Ebarrier\n")
        hopping_path_list_tmp = []
        hopping_energy_tmp = []
        for ipath1,path1 in enumerate(path_candidates):
            fn1 = filename_candidates[ipath1]
            Ebarrier1 = 1e10
            for i1 in range(len(path1)-1):
                atom_id1 = path1[i1]
                atom_id2 = path1[i1+1]
                symb1 = symbols_supercell[atom_id1-1]
                symb2 = symbols_supercell[atom_id2-1]
                if atom_id1 < atom_id2:
                    hop12 = (symb1,symb2)
                    id_atom12 = (atom_id1,atom_id2)
                else:
                    hop12 = (symb2,symb1)
                    id_atom12 = (atom_id2,atom_id1)
                coords1 = coords_supercell[atom_id1-1]
                coords2 = coords_supercell[atom_id2-1]
                dv21 = np.array(coords2) - np.array(coords1)
                for j1 in range(3):
                    if dv21[j1] < -0.5:
                        dv21[j1] += 1.0
                    if dv21[j1] >= +0.5:
                        dv21[j1] -= 1.0
                dv21_cart = lc2 @ dv21
                dist1 = np.linalg.norm(dv21_cart)
                dv21_unit = dv21_cart/dist1
                coords1_cart = lc2 @ np.array(coords1) 
                coords2_cart = lc2 @ np.array(coords2)

                fout.write(f"{ipath1+1:04d},{fn1},{atom_id1},{atom_id2},{symb1},{symb2},{dist1:.6f}")
                Ebarrier = 0.0
                Ebarrier_min = 1e10
                if bvse_calc:
                    ### search bvse-Ebarrier along the path
                    nline = int(np.floor(dist1/bvse_singleHop_delx))
                    delx = dist1/nline
                    line_hopping = np.linspace(0,dist1,nline)
                    print(f"      BVSE calc. for path {ipath1+1:04d}: {atom_id1}({symb1})->{atom_id2}({symb2})")
                    print(f"        {coords1} -> {coords2}")
                    print(f"        distance: {dist1:.6f}")
                    print(f"        The number of line_hopping: {len(line_hopping)}")
                    bvse_Ebarrier_list = []
                    for d1 in line_hopping:
                        coords_tmp0 = coords1_cart + d1*dv21_unit
                        Ebarrier_tmp = []
                        for d2 in bvse_coords_in_circle:
                            d2_vec = np.array([d2[0], d2[1], 0.0])
                            z_axis = np.array([0.0, 0.0, 1.0])
                            if np.allclose(dv21_unit, z_axis):
                                d3 = d2_vec
                            elif np.allclose(dv21_unit, -z_axis):
                                rot = R.from_rotvec(np.pi * np.array([1, 0, 0]))
                                d3 = rot.apply(d2_vec)
                            else:
                                rot, _ = R.align_vectors([dv21_unit], [z_axis])
                                d3 = rot.apply(d2_vec)
                            coords_tmp1 = coords_tmp0 + d3
                            coords_tmp2 = np.linalg.inv(latt_const_supercell) @ coords_tmp1
                            for j1 in range(3):
                                if coords_tmp2[j1] < 0.0:
                                    coords_tmp2[j1] += 1.0
                                if coords_tmp2[j1] >= 1.0:
                                    coords_tmp2[j1] -= 1.0
                            v2 = vol_super.value_at(x=coords_tmp2[0],y=coords_tmp2[1],z=coords_tmp2[2])
                            Ebarrier_tmp.append(v2)
                        bvse_Ebarrier_list.append(min(Ebarrier_tmp))
                    bvse_Ebarrier_list = np.array(bvse_Ebarrier_list)-bvse_val_min
                    Ebarrier_min = bvse_Ebarrier_list.max()
                    print(f"      Ebarrier: {Ebarrier_min:.6f}")
                    fout.write(f",{Ebarrier_min:.6f}\n")
                    if bvse_plot_singleHopping:
                        plt.plot(line_hopping,bvse_Ebarrier_list,color="blue",lw=2.0)
                        plt.xlabel(r"Position on the path ($\AA$)",fontsize=12)
                        plt.ylabel(r"Energy (eV)",fontsize=12)
                        plt.xlim([0,dist1])
                        plt.ylim([0,Ebarrier_min*1.1])
                        plt.tick_params(labelsize=10)
                        plt.title(f"BVSE along the path ({ipath1+1:04d}): {atom_id1}({symb1})->{atom_id2}({symb2})",size=12)
                        plt.tight_layout()
                        plt.grid(True)
                        fn = f"out_bvse_singleHopping_{ipath1+1:04d}_{atom_id1}to{atom_id2}.png"
                        fnpath = os.path.join(folder_path,fn)
                        plt.savefig(fnpath)
                        plt.close()
                        print(f"      The plot for single hopping is saved as {fn}")
                else:
                    fout.write("\n")
                bool_already = False
                for hop12_tmp,id_atom12_tmp,dist1_tmp,Ebarrier_tmp in hopping_path_list_tmp:
                    dist1_diff = abs(dist1-dist1_tmp)
                    if hop12_tmp == hop12 and dist1_diff < 0.00001:
                        bool_already = True
                        break
                if not bool_already:
                    hopping_path_list_tmp.append((hop12,id_atom12,dist1,Ebarrier_min))
                if Ebarrier_min < Ebarrier1:
                    Ebarrier1 = Ebarrier_min
            hopping_energy_tmp.append(Ebarrier1)
        fout.close()
        hopping_path_list_tmp = list(dict.fromkeys(hopping_path_list_tmp))

        fnout = os.path.join(folder_path, "out_paths_candidates.csv")
        print(f"    Number of paths candidates: {len(path_candidates)}")
        print(f"    Writing paths candidates into {fnout}")
        fout = open(fnout, "w")
        fout.write(f"path-id,filename,path,distance,Ebarrier\n")
        for ip1 in range(len(path_candidates)):
            fout.write(f"{ip1+1:04d},{filename_candidates[ip1]},{path_candidates_str[ip1]},{dist_candidates[ip1]},{hopping_energy_tmp[ip1]:.6f}\n")
        fout.close()

        print("-"*50)
        os.chdir("../")
        print(f"    Number of indipendent single hopping paths: {len(hopping_path_list_tmp)}")
        fout = open("out005_singleHoppingPaths.csv", "w")
        print(f"    Writing single hopping paths into {fout.name}")
        fout.write(f"id,site1,site2,atom_id1,atom_id2,distance,Ebarrier\n")
        id_hopping = 1
        for hop12_tmp,id12_tmp,dist1_tmp,Ebarrier_tmp in hopping_path_list_tmp:
            fout.write(f"{id_hopping:04d},{hop12_tmp[0]},{hop12_tmp[1]},{id12_tmp[0]},{id12_tmp[1]},{dist1_tmp:.6f},{Ebarrier_tmp:.6f}\n")
            id_hopping += 1
            bool_already = False
            for hop12,id12,dist1,Ebarrier1 in hopping_path_list:
                dist1_diff = abs(dist1-dist1_tmp)
                if hop12_tmp == hop12 and dist1_diff < 0.00001:
                    bool_already = True
                    break
            if not bool_already:
                hopping_path_list.append((hop12_tmp,id12_tmp,dist1_tmp,Ebarrier_tmp))
        fout.close()
        print(f"-"*50)
        os.chdir("../")
    os.chdir("../")
    print("  Finished.")

def search_paths():
    input_template_searchPaths="""
input_POSCAR = "***.vasp"
supercell = [2,2,2]
# clean_dpath = true

migrating_element = "Li"
vacancy_migration = true
# interstitial_migration = true
# skip_neighbor_search = true

# max_concerted_sites = 2
# cutoffR_neigh_base = 4.0
# cutoffR_neigh.Rn_Rn = 6.0
# skip_chkdupl = true
# tolerance_chkDupl = 0.001
    """
    print("Starting pydecs-dpath-search-paths")
    argparser = argparse.ArgumentParser(
        description="""This tool searches paths from a given POSCAR file with grouped site-symmetry labels, 
         generating inpydecs_paths_list.csv file""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    argparser.add_argument(
        "input_toml", 
        type=str, 
        help="Input toml file (default: inpydecs_searchPaths.toml)",
        nargs="?",
        default="inpydecs_searchPaths.toml",
        )
    argparser.add_argument(
        "-p", "--printOut_inputTemplate", 
        action="store_true",
        help="Print out input-file template: inpydecs_searchPaths.csv"
        )
    args = argparser.parse_args()
    input_toml = args.input_toml
    if args.printOut_inputTemplate:
        fname = "inpydecs_searchPaths.toml"
        if os.path.exists(fname):
            print(f"  {fname} already exists.")
            print("  The template is as follows:")
            print("#"*50)
            print(input_template_searchPaths.strip())
            print("#"*50)
        else:
            print(f"  Creating {fname}.")
            with open(fname, "w") as f:
                f.write(input_template_searchPaths.strip() + "\n")
            print(f"  {fname} has been created.")
        sys.exit()
    print("  "+"-"*50)
    print(f"  Reading input toml file: {input_toml}")
    if not os.path.exists(input_toml):
        print(f"  Error!! {input_toml} not found.")
        print("  Please create the file with -p option.")
        print(f"  $ pydecs-dpath-search-paths -p")
        sys.exit()
    with open(input_toml, 'r') as f:
        config_in = toml.load(f)
    if 'input_POSCAR' not in config_in:
        raise KeyError("The 'input_POSCAR' tag is required in the configuration file.")
    input_POSCAR = config_in['input_POSCAR']
    if not 'supercell' in config_in:
        print("  Error!! supercell is not set. Please set it in the configuration file.")
        sys.exit()
    supercell = config_in['supercell']
    if not (
        isinstance(supercell, list) 
        and len(supercell) == 3 
        and all(isinstance(x, int) for x in supercell)
    ):
        print("  Error!! 'supercell' must be a list of three integers: [int, int, int].")
        sys.exit()
    clean_dpath = False
    if 'clean_dpath' in config_in:
        clean_dpath = config_in['clean_dpath']
    if not 'migrating_element' in config_in:
        print("  Error!! 'migrating_element' is not set. Please set it in the configuration file.")
        sys.exit()
    migrating_element = config_in['migrating_element']
    vacancy_migration = False
    if 'vacancy_migration' in config_in:
        vacancy_migration = config_in['vacancy_migration']
    interstitial_migration = False
    if 'interstitial_migration' in config_in:
        interstitial_migration = config_in['interstitial_migration']
    skip_neighbor_search = False
    if 'skip_neighbor_search' in config_in:
        skip_neighbor_search = config_in['skip_neighbor_search']
    max_concerted_sites = 2
    if 'max_concerted_sites' in config_in:
        max_concerted_sites = config_in['max_concerted_sites']
    if max_concerted_sites < 2:
        print("  Error!! max_concerted_sites must be greater than or equal to 2.")
        sys.exit()
    cutoffR_neigh_base = 3.0
    if 'cutoffR_neigh_base' in config_in:
        cutoffR_neigh_base = config_in['cutoffR_neigh_base']
    cutoffR_neigh = {}
    for ls1 in [migrating_element, "Rn"]:
        for ls2 in [migrating_element, "Rn"]:
            cutoffR_neigh[f"{ls1}_{ls2}"] = cutoffR_neigh_base
    if 'cutoffR_neigh' in config_in:
        for cutoffR_key, cutoffR_value in config_in['cutoffR_neigh'].items():
            cutoffR_neigh[cutoffR_key] = cutoffR_value
            elems_key = cutoffR_key.split("_")
            #if elems_key[0] != elems_key[1]:
            #    cutoffR_key_inverted = f"{elems_key[1]}_{elems_key[0]}"
            #    cutoffR_neigh[cutoffR_key_inverted] = cutoffR_value
    tolerance_chkDupl = 0.001
    if 'tolerance_chkDupl' in config_in:
        tolerance_chkDupl = config_in['tolerance_chkDupl']
    skip_chkdupl = False
    if 'skip_chkdupl' in config_in:
        skip_chkdupl = config_in['skip_chkdupl']

    print("  Parameters:")
    print(f"    input_POSCAR: {input_POSCAR}")
    print(f"    supercell: {supercell}")
    print(f"    clean_dpath: {clean_dpath}")
    print(f"    migrating_element: {migrating_element}")
    print(f"    vacancy_migration: {vacancy_migration}")
    print(f"    interstitial_migration: {interstitial_migration}")
    print(f"    skip_neighbor_search: {skip_neighbor_search}")
    print(f"    max_concerted_sites: {max_concerted_sites}")
    print(f"    cutoffR_neigh: {cutoffR_neigh}")
    print(f"    tolerance_chkDupl: {tolerance_chkDupl}")
    print(f"    skip_chkdupl: {skip_chkdupl}")
    print("  "+"-"*50)
    if clean_dpath:
        print("  Cleaning the dpath folders")
        os.system("rm -rf dpath*")
    else:
        print("  dpath folders are not cleaned up.")
    print("  "+"-"*50)

    # Reading POSCAR
    print(f"  Reading input POSCAR file: {input_POSCAR}")
    latt_const0, coords0, symbols0, type_grouped0 = parse_poscar_dpath(input_POSCAR)
    if not type_grouped0:
        print(f"    Error!! not supported for ungrouped POSCAR with site-symmetry labels like {symbols0[0]}.")
        print("    Please use ungrouped POSCAR file.")
        sys.exit()
    lattSites_list0 = list(OrderedDict.fromkeys(symbols0))
    nLattSites0 = [symbols0.count(e1) for e1 in lattSites_list0]
    print(f"    Number of atoms: {len(coords0)}")
    print(f"    Lattice sites: {lattSites_list0}")
    print(f"    Number of each lattice site: {nLattSites0}")
    print("    Lattice constants: ")
    for i1 in range(3):
        str_lc = "      "
        for i2 in range(3):
            str_lc += f"{latt_const0[i1][i2]:10.6f} "
        print(str_lc)
    print("  "+"-"*50)
    bool_check = False
    migrating_element_sites = []
    interstitial_sites = []
    for ls1 in lattSites_list0:
        if migrating_element == ls1[:ls1.find("[")]:
            bool_check = True
            migrating_element_sites.append(ls1)
        if "Rn" in ls1[:ls1.find("[")]:
            interstitial_sites.append(ls1)
    if not bool_check:
        print(f"  migrating_element: {migrating_element} is not included in the input POSCAR file.")
        # sys.exit()

    # generating supercell
    print(f"  Generating supercell structure")
    latt_const1 = latt_const0 * np.array(supercell)
    symbols1 = []
    coords1 = []
    for i1 in range(len(coords0)):
        s1 = symbols0[i1]
        c1 = coords0[i1]
        for ic1, ic2, ic3 in product(range(supercell[0]), range(supercell[1]), range(supercell[2])):
            symbols1.append(s1)
            c2_1 = (c1[0] + ic1)/float(supercell[0])
            c2_2 = (c1[1] + ic2)/float(supercell[1])
            c2_3 = (c1[2] + ic3)/float(supercell[2])
            c2 = np.array([c2_1, c2_2, c2_3])
            coords1.append(c2)
    lattSites_list1 = list(OrderedDict.fromkeys(symbols1))
    nLattSites1 = [symbols1.count(e1) for e1 in lattSites_list1]
    print(f"    Number of atoms: {len(coords1)}")
    print(f"    Lattice sites: {lattSites_list1}")
    print(f"    Number of each lattice site: {nLattSites1}")
    print("    Lattice constants: ")
    for i1 in range(3):
        str_lc = "      "
        for i2 in range(3):
            str_lc += f"{latt_const1[i1][i2]:10.6f} "
        print(str_lc)
    output_vasp("dpath_supercell.vasp", {"cell": latt_const1, "elements": symbols1, "coords": coords1})
    print(f"    Saved supercell structure as 'supercell.vasp'")
    print("="*50,flush=True)

    def extract_position_near_center(ls1_in):
        idmig1 = -1
        cmig1 = None
        dmin1 = 1e10
        for i1, (s1, c1) in enumerate(zip(symbols1, coords1)):
            if s1 != ls1_in:
                continue
            c2 = [c1[0]-0.5, c1[1]-0.5, c1[2]-0.5]
            for j1 in range(3):
                if c2[j1] < -0.5:
                    c2[j1] += 1.0
                if c2[j1] >= 0.5:
                    c2[j1] -= 1.0
            c2abs = np.linalg.norm(c2)
            if c2abs < dmin1:
                dmin1 = c2abs
                idmig1 = i1
                cmig1 = c1
        return idmig1, cmig1, dmin1

    def extract_neighbors(idmig1_in):
        neighbors1 = []
        c1 = coords1[idmig1_in]
        s1 = symbols1[idmig1_in]
        e1 = s1[:s1.find("[")]
        for i2, (s2, c2) in enumerate(zip(symbols1, coords1)):
            e2 = s2[:s2.find("[")]
            if e2 != migrating_element and e2 != "Rn":
                continue
            if idmig1_in == i2:
                continue
            c21_diff = c2-c1
            for j1 in range(3):
                if c21_diff[j1] < -0.5:
                    c21_diff[j1] += 1.0
                if c21_diff[j1] >= 0.5:
                    c21_diff[j1] -= 1.0
            c21_diff_cart = c21_diff @ latt_const1
            c21_diff_cart_abs = np.linalg.norm(c21_diff_cart)
            if c21_diff_cart_abs < cutoffR_neigh[f"{e1}_{e2}"]:
                # print(f"    {s1}_{s2}: {c21_diff_cart_abs}")

                neighbors1.append({"id": i2, "symbol": s2, "elem": e2, "coord": c2, "dist": c21_diff_cart_abs})
        sorted_neighbors1 = sorted(neighbors1, key=lambda x: x["dist"])
        return sorted_neighbors1

    # Neighbor search for each site
    if not skip_neighbor_search:
        print(f"  Searching neighbors for each site")
        fol1 = "dpath_neighbors"
        if not os.path.exists(fol1):
            os.makedirs(fol1)
        os.chdir(fol1)
        for ls1 in lattSites_list1:
            e1 = ls1[:ls1.find("[")]
            if e1 != migrating_element and e1 != "Rn":
                continue
            idmig1, cmig1, dmin1 = extract_position_near_center(ls1)
            print(f"    Searcning for {ls1}(atom-id:{idmig1+1}) at {cmig1}")
            # print(f"    {ls1}, {idmig1+1}, {cmig1}, {dmin1}")
            neighbors1 = extract_neighbors(idmig1)
            # print(f"    Neighbors: {neighbors1}")
            # Make sure we open the file in write mode only once, outside the loop
            csv_filename = f"dpath_neighbors_{ls1}.csv"
            write_header = not os.path.exists(csv_filename)
            with open(csv_filename, mode='a', newline='') as csvfile:
                fieldnames = [
                    "center_id_from0", "center_symbol", "center_elem", "center_coord", 
                    "neighbor_id_from0", "neighbor_symbol", "neighbor_elem", "neighbor_coord", "neighbor_dist"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                # For each ls1, write its neighbors to csv
                center_symbol = ls1
                center_elem = e1
                center_id = idmig1
                center_coord = cmig1.tolist() if hasattr(cmig1, "tolist") else cmig1
                for neigh in neighbors1:
                    row = {
                        "center_id_from0": center_id,
                        "center_symbol": center_symbol,
                        "center_elem": center_elem,
                        "center_coord": center_coord,
                        "neighbor_id_from0": neigh["id"],
                        "neighbor_symbol": neigh["symbol"],
                        "neighbor_elem": neigh["elem"],
                        "neighbor_coord": neigh["coord"].tolist() if hasattr(neigh["coord"], "tolist") else neigh["coord"],
                        "neighbor_dist": neigh["dist"],
                    }
                    writer.writerow(row)
        os.chdir("..")
    else:
        print(f"  Skipping neighbor search.")
    print("="*50,flush=True)

    # Recursive search for both migration
    def recursive_search_concerted_migration(idmig1_in,type_migration_in,paths_list_in,path_symbols_in,path_ids_from0_in):
        c1 = coords1[idmig1_in]
        s1 = symbols1[idmig1_in]
        e1 = s1[:s1.find("[")]
        neighbors1 = extract_neighbors(idmig1_in)
        for neigh in neighbors1:
            idmig2 = neigh["id"]
            s2 = neigh["symbol"]
            e2 = neigh["elem"]
            c2 = neigh["coord"]
            dist = neigh["dist"]
            if type_migration_in == "vacancy":
                if e2 != migrating_element:
                    continue
                path_symbols2 = path_symbols_in + f"{s2}"
                path_ids_from02 = path_ids_from0_in + [idmig2]
                if idmig2 in path_ids_from0_in:
                    continue
                paths_list_in.append({"symbols": path_symbols2, "ids_from0": path_ids_from02})
                if len(path_ids_from0_in) < max_concerted_sites-1:
                    recursive_search_concerted_migration(idmig2, "vacancy", paths_list_in, path_symbols2+"-", path_ids_from02)

            if type_migration_in == "interstitial":
                if e2 == "Rn":
                    path_symbols2 = path_symbols_in + f"{s2}"
                    path_ids_from02 = path_ids_from0_in + [idmig2]
                    if idmig2 == path_ids_from0_in[0] and len(path_ids_from0_in) == 2:
                        continue
                    paths_list_in.append({"symbols": path_symbols2, "ids_from0": path_ids_from02})
                elif e2==migrating_element:
                    if len(path_ids_from0_in) < max_concerted_sites-1:
                        path_symbols2 = path_symbols_in + f"{s2}"
                        path_ids_from02 = path_ids_from0_in + [idmig2]
                        if idmig2 in path_ids_from0_in:
                            continue
                        recursive_search_concerted_migration(idmig2, "interstitial", paths_list_in, path_symbols2+"-", path_ids_from02)

    # Searching paths for vacancy_migration
    if vacancy_migration:
        print(f"  Searching paths for migration of {migrating_element} vacancy")
        fol1 = "dpath_search_vacancy_migration"
        if not os.path.exists(fol1):
            os.makedirs(fol1)
        os.chdir(fol1)
        folname_eachNs = []
        cnt_files = []
        out_paths_list = []
        for ica1 in range(max_concerted_sites-1):
            fol1 = f"strs0_all_Nsites{ica1+2:02d}"
            folname_eachNs.append(fol1)
            if not os.path.exists(fol1):
                os.makedirs(fol1)
            cnt_files.append(1)
            f1 = open(f"{fol1}/out_paths_list_{ica1+2:02d}.csv", "w")
            f1.write("filename,NmigSites,path_symbols,ids_from0\n")
            out_paths_list.append(f1)
        for ls1 in migrating_element_sites:
            print(f"  Searching paths for {ls1}")
            idmig1, cmig1, dmin1 = extract_position_near_center(ls1)
            print(f"    Searcning for {ls1}(atom-id:{idmig1+1}) at {cmig1}")
            paths_list = []
            path_symbols = f"{ls1}-"
            path_ids_from0 = [idmig1]
            recursive_search_concerted_migration(idmig1, "vacancy", paths_list, path_symbols,path_ids_from0)
            # print(paths_list)
            print(f"    Number of all detected paths: {len(paths_list)}")
            for ica1 in range(max_concerted_sites-1):
                paths_list_tmp = []
                for p1 in paths_list:
                    if len(p1["ids_from0"]) == ica1+2:
                        paths_list_tmp.append(p1)
                print(f"    Number of paths with {ica1+2} sites: {len(paths_list_tmp)}")
                for p1 in paths_list_tmp:
                    symbols2 = copy.deepcopy(symbols1)
                    coords2 = copy.deepcopy(coords1)
                    ids_from0_tmp = p1["ids_from0"]
                    path_symbols_tmp = p1["symbols"]
                    for id2 in ids_from0_tmp:
                        symbols2[id2] = "Fr"
                    fnoutvasp = f"strs0_all_Nsites{ica1+2:02d}/POSCAR_{cnt_files[ica1]:04d}.vasp"
                    coords3 = []
                    symbols3 = []
                    for s2,c2 in zip(symbols2,coords2):
                        if s2[:s2.find("[")] != "Rn":
                            coords3.append(c2)
                            symbols3.append(s2)
                    output_vasp(fnoutvasp, {"cell": latt_const1, "elements": symbols3, "coords": coords3})
                    out_paths_list[ica1].write(f"{fnoutvasp},{ica1+2},{path_symbols_tmp},\"{ids_from0_tmp}\" \n")
                    cnt_files[ica1] += 1
                    print(f"    Saved {fnoutvasp}",flush=True)
            print("  "+"-"*30)
        for ica1 in range(max_concerted_sites-1):
            out_paths_list[ica1].close()
        fout_pathslist = open("inpydecs_paths_list_vacancy.csv", "w") 
        fout_pathslist.write("id,atom_id1,site1,atom_id2,site2,elem_diff\n")
        id_pathlist = 1
        for ica1 in range(max_concerted_sites-1):
            os.chdir(folname_eachNs[ica1])
            if not skip_chkdupl:
                path3 = f"POSCAR_*.vasp"
                print(f"    Running duplication check for {folname_eachNs[ica1]}",flush=True)
                sys.argv = [
                        "pydecs-prep-chkDupl",
                        "-t",str(tolerance_chkDupl),
                        *glob.glob(path3),
                        ]
                check_duplication()
                fn_dup = "out_duplication.csv"
                if not os.path.exists(fn_dup):
                    print(f"  Warning!! out_duplication.csv is not found. Skipped.")
                    continue
                fn_vasp_list=[t1.strip() for t1 in open(fn_dup).readlines()[1].split(",")]
                folder_up = os.path.abspath(os.path.join("..", f"strs1_symInd_Nsites{ica1+2:02d}"))
                if not os.path.exists(folder_up):
                    os.makedirs(folder_up)
                idlist_path = []
                for fn_vasp in fn_vasp_list:
                    shutil.copy(fn_vasp, folder_up)
                    idlist_path.append(int(fn_vasp.split("_")[1].split(".")[0]))
                fin1 = open(f"out_paths_list_{ica1+2:02d}.csv").readlines()
                fout1 = open(f"{folder_up}/out_paths_list_{ica1+2:02d}_symInd.csv", "w")
                fout1.write(fin1[0])
                for il1,l1 in enumerate(fin1):
                    if il1 in idlist_path:
                        fout1.write(l1)
                        idatom_list2 = l1[l1.find("\"[")+2:l1.rfind("]\"")].split(",")
                        idatom_list2 = [int(t1)+1 for t1 in idatom_list2]
                        sites_list2 = l1.split(",")[2].split("-")
                        for j3 in range(len(idatom_list2)-1):
                            id3 = idatom_list2[j3]
                            id3next = idatom_list2[j3+1]
                            site3 = sites_list2[j3]
                            site3next = sites_list2[j3+1]
                            fout_pathslist.write(f"{id_pathlist},{id3},{site3},{id3next},{site3next},{migrating_element}\n")
                        id_pathlist += 1
                fout1.close()
            fout_pathslist.flush()
            os.chdir("..")
        fout_pathslist.close()
        os.chdir("..")
    else:
        print(f"  No vacancy migration paths are searched.")
    print("="*50,flush=True)
    
    # Searching paths for interstitial_migration
    if interstitial_migration:
        print(f"  Searching paths for interstitial_migration")
        fol1 = "dpath_search_interstitial_migration"
        if not os.path.exists(fol1):
            os.makedirs(fol1)
        os.chdir(fol1)
        folname_eachNs = []
        cnt_files = []
        out_paths_list = []
        for ica1 in range(max_concerted_sites-1):
            fol1 = f"strs0_all_Nsites{ica1+2:02d}"
            print(fol1)
            folname_eachNs.append(fol1)
            if not os.path.exists(fol1):
                os.makedirs(fol1)
            cnt_files.append(1)
            f1 = open(f"{fol1}/out_paths_list_{ica1+2:02d}.csv", "w")
            f1.write("filename,NmigSites,path_symbols,ids_from0\n")
            out_paths_list.append(f1)
        for ls1 in interstitial_sites:
            print(f"  Searching paths for {ls1}")
            idmig1, cmig1, dmin1 = extract_position_near_center(ls1)
            print(f"    Searcning for {ls1}(atom-id:{idmig1+1}) at {cmig1}")
            paths_list = []
            path_symbols = f"{ls1}-"
            path_ids_from0 = [idmig1]
            recursive_search_concerted_migration(idmig1, "interstitial", paths_list, path_symbols,path_ids_from0)
            # print(paths_list)
            print(f"    Number of all detected paths: {len(paths_list)}")
            for ica1 in range(max_concerted_sites-1):
                paths_list_tmp = []
                for p1 in paths_list:
                    if len(p1["ids_from0"]) == ica1+2:
                        paths_list_tmp.append(p1)
                print(f"    Number of paths with {ica1+2} sites: {len(paths_list_tmp)}")
                for p1 in paths_list_tmp:
                    symbols2 = copy.deepcopy(symbols1)
                    coords2 = copy.deepcopy(coords1)
                    ids_from0_tmp = p1["ids_from0"]
                    path_symbols_tmp = p1["symbols"]
                    for id2 in ids_from0_tmp:
                        symbols2[id2] = "Fr"
                    fnoutvasp = f"strs0_all_Nsites{ica1+2:02d}/POSCAR_{cnt_files[ica1]:04d}.vasp"
                    coords3 = []
                    symbols3 = []
                    for s2,c2 in zip(symbols2,coords2):
                        if s2[:s2.find("[")] != "Rn":
                            coords3.append(c2)
                            symbols3.append(s2)
                    output_vasp(fnoutvasp, {"cell": latt_const1, "elements": symbols3, "coords": coords3})
                    out_paths_list[ica1].write(f"{fnoutvasp},{ica1+2},{path_symbols_tmp},\"{ids_from0_tmp}\" \n")
                    cnt_files[ica1] += 1
                    print(f"    Saved {fnoutvasp}",flush=True)
            print("  "+"-"*30)
        for ica1 in range(max_concerted_sites-1):
            out_paths_list[ica1].close()
        fout_pathslist = open("inpydecs_paths_list_interstitial.csv", "w")
        fout_pathslist.write("id,atom_id1,site1,atom_id2,site2,elem_diff\n")
        id_pathlist = 1
        for ica1 in range(max_concerted_sites-1):
            os.chdir(folname_eachNs[ica1])
            if not skip_chkdupl:
                path3 = f"POSCAR_*.vasp"
                print(f"    Running duplication check for {folname_eachNs[ica1]}",flush=True)
                sys.argv = [
                        "pydecs-prep-chkDupl",
                        "-t",str(tolerance_chkDupl),
                        *glob.glob(path3),
                        ]
                check_duplication()
                fn_dup = "out_duplication.csv"
                if not os.path.exists(fn_dup):
                    print(f"  Warning!! out_duplication.csv is not found. Skipped.")
                    continue
                fn_vasp_list=[t1.strip() for t1 in open(fn_dup).readlines()[1].split(",")]
                folder_up = os.path.abspath(os.path.join("..", f"strs1_symInd_Nsites{ica1+2:02d}"))
                if not os.path.exists(folder_up):
                    os.makedirs(folder_up)
                idlist_path = []
                for fn_vasp in fn_vasp_list:
                    shutil.copy(fn_vasp, folder_up)
                    idlist_path.append(int(fn_vasp.split("_")[1].split(".")[0]))
                fin1 = open(f"out_paths_list_{ica1+2:02d}.csv").readlines()
                fout1 = open(f"{folder_up}/out_paths_list_{ica1+2:02d}_symInd.csv", "w")
                fout1.write(fin1[0])
                for il1,l1 in enumerate(fin1):
                    if il1 in idlist_path:
                        fout1.write(l1)
                        idatom_list2 = l1[l1.find("\"[")+2:l1.rfind("]\"")].split(",")
                        idatom_list2 = [int(t1)+1 for t1 in idatom_list2]
                        sites_list2 = l1.split(",")[2].split("-")
                        for j3 in range(len(idatom_list2)-1):
                            id3 = idatom_list2[j3]
                            id3next = idatom_list2[j3+1]
                            site3 = sites_list2[j3]
                            site3next = sites_list2[j3+1]
                            fout_pathslist.write(f"{id_pathlist},{id3},{site3},{id3next},{site3next},{migrating_element}\n")
                        id_pathlist += 1
                fout1.close()
            fout_pathslist.flush()
            os.chdir("..")
        fout_pathslist.close()
        os.chdir("..")            
    else:
        print(f"  No interstitial migration paths are searched.")
    print("="*50,flush=True)


def mkimages_from_twoposcars():
    print("Starting pydecs-dpath-mkimages-twoPOSCARs")
    argparser = argparse.ArgumentParser()
    argparser.add_argument("init_poscar", type=str, help="Initial POSCAR file")
    argparser.add_argument("final_poscar", type=str, help="Final POSCAR file")
    argparser.add_argument("-n", "--n_images", type=int, default=3, help="The number of images")
    argparser.add_argument("-t", "--tol_diff", type=float, default=0.1, help="The tolerance for diffusing atoms")
    argparser.add_argument("-i", "--idpp", action="store_true", help="IDPP")
    argparser.add_argument("-o", "--filename_outcomb", type=str, default="out_mark_diffusing_species.vasp", help="Ouput combined POSCAR file")
    args = argparser.parse_args()
    filename_outcomb = args.filename_outcomb
    tol_diff = args.tol_diff
    init_poscar = args.init_poscar
    final_poscar = args.final_poscar
    n_images = args.n_images
    idpp = args.idpp

    if not os.path.exists(init_poscar):
        print(f"Error: File not found: {init_poscar}")
        sys.exit(1)
    if not os.path.exists(final_poscar):
        print(f"Error: File not found: {final_poscar}")
        sys.exit(1)

    print("  Parameters:")
    print(f"    Init_poscar: {init_poscar}")
    print(f"    Final_poscar: {final_poscar}")
    print(f"    n_images: {n_images}")
    print(f"    filename_outcomb: {filename_outcomb}")
    print(f"    tol_diff: {tol_diff}")
    print(f"    IDPP: {idpp}")
    print("  "+"-"*50)

    try:
        from ase.io import read, write
        from ase.mep import NEB
        from ase.io.vasp import write_vasp
    except ImportError:
        print("  Error: ase is not installed.")
        sys.exit(1)
    initial = read(init_poscar)
    final   = read(final_poscar)
    images = [initial] + [initial.copy() for _ in range(n_images)] + [final]
    neb = NEB(images)
    if idpp:
        neb.interpolate(method='idpp',mic=True)
    else:
        neb.interpolate(method='linear',mic=True)
    coords_images = []
    for i1,im1 in enumerate(images):
        folder = f"{i1:02d}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        fn = os.path.join(folder, "POSCAR")
        write_vasp(fn,im1,direct=True)
        print(f"    Outputting image {i1:02d} to {fn}")
        coords_images.append(im1.get_scaled_positions())
    print("  "+"-"*50)

    ### making overlapping structure ###
    elements_all_list = initial.get_chemical_symbols()
    latt_const = initial.cell[:]
    elems = list(OrderedDict.fromkeys(elements_all_list))
    num_atoms = [elements_all_list.count(e1) for e1 in elems]
    print("  Detecting diffusing atoms:")
    print(f"    Elements: {elems}")
    print(f"    Number of atoms: {num_atoms}")
    ids_diffusing = []
    for i1 in range(len(coords_images[0])):
        diff1 = np.array(coords_images[-1][i1]) - np.array(coords_images[0][i1])
        for j1 in range(3):
            if diff1[j1] < -0.5:
                diff1[j1] += 1.0
            if diff1[j1] >= +0.5:
                diff1[j1] -= 1.0
        diff1_cart = latt_const @ diff1
        dist1 = np.linalg.norm(diff1_cart)
        if dist1 > tol_diff:
            ids_diffusing.append(i1)
    print(f"    Diffusing atoms:")
    for i1 in ids_diffusing:
        print(f"      atom-ID: {i1+1} ({elements_all_list[i1]})")
    coords_comb = []
    elements_list_comb = []
    labels_diffusing = ["Fr","Ra","Ac","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og"]
    for i1 in range(len(coords_images[0])):
        if i1 in ids_diffusing:
            idx_diff = ids_diffusing.index(i1)
            for im1 in range(n_images + 2): 
                rand_vect = np.array([np.random.rand()*1e-3, np.random.rand()*1e-3, np.random.rand()*1e-3])
                coords_comb.append(coords_images[im1][i1]+rand_vect)
                # print(f"      {i1+1}, {im1}: {coords_images[im1][i1]+rand_vect}, {rand_vect}")
                elements_list_comb.append(labels_diffusing[idx_diff])
        else:
            coords_comb.append(coords_images[0][i1])
            elements_list_comb.append(elements_all_list[i1])
    structure_comb = {
        "cell": latt_const,
        "elements": elements_list_comb,
        "coords": coords_comb,
    }
    output_vasp(filename_outcomb, structure_comb, coords_are_cartesian=False)
    print(f"    Outputting the combined structure to {filename_outcomb}")
    print(f"      In this representation, small random shifts are added to the diffusing atoms")
    print(f"        for visualizing the duplicated diffusing atoms in the VESTA file.")
    print("  Finished.")

def mkimages_from_pathsfile():
    print("Starting pydecs-dpath-mkimages-pathsfile")
    argparser = argparse.ArgumentParser(
        description="""Make images from inpydecs_paths_list.csv file
    Required headers in the inpydecs_paths_list.csv file: 
        > id, atom_id1, atom_id2, elem_diff
        > Example:
        >   id, atom_id1, atom_id2, elem_diff
        >   1 ,   80    ,    92   ,   F""",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    argparser.add_argument(
        "input_poscar", 
        type=str, 
        help="Input supercell-POSCAR (without grouped site-symmetry labels)")
    argparser.add_argument(
        "-p","--paths_list", 
        type=str, 
        help="Paths list file (csv format, default: ipydecs_paths_list.csv)",
        default="inpydecs_paths_list.csv")
    argparser.add_argument("-n", "--n_images", type=int, default=3, help="The number of images")
    argparser.add_argument("-o", "--filename_outcomb", type=str, default="out_mark_diffusing_species.vasp", help="Ouput combined POSCAR file")
    argparser.add_argument("-t", "--tol_diff", type=float, default=0.1, help="The tolerance for diffusing atoms")
    args = argparser.parse_args()
    paths_list = args.paths_list
    filename_outcomb = args.filename_outcomb
    input_poscar = args.input_poscar

    tol_diff = args.tol_diff
    n_images = args.n_images

    print("  Parameters:")
    print(f"    Input POSCAR file: {input_poscar}")
    print(f"    Paths list file: {paths_list}")
    print(f"    n_images: {n_images}")
    print(f"    filename_outcomb: {filename_outcomb}")
    print(f"    tol_diff: {tol_diff}")

    print("  "+"-"*50)
    print(f"  Reading input POSCAR file: {input_poscar}")
    latt_const0, coords0, symbols0, type_grouped0 = parse_poscar_dpath(input_poscar)
    if type_grouped0:
        print(f"    Error!! not supported for grouped POSCAR with site-symmetry labels like {symbols0[0]}.")
        print("    Please use ungrouped POSCAR file.")
        sys.exit()
    elems_list0 = list(OrderedDict.fromkeys(symbols0))
    natoms0 = [symbols0.count(e1) for e1 in elems_list0]
    print(f"    Number of atoms: {len(coords0)}")
    print(f"    Elements: {elems_list0}")
    print(f"    Number of each atom type: {natoms0}")
    print("  "+"-"*50)
    print(f"  Reading paths_list file: {paths_list}",flush=True)
    migrating_id_list = []
    migrating_elems_list = {}
    migrating_atoms_list = {}
    with open(paths_list, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for row in reader:
            try:
                id_list_tmp = int(row["id"])
                atom_id1_tmp = int(row["atom_id1"])
                atom_id2_tmp = int(row["atom_id2"])
                elem_diff_tmp = row["elem_diff"].strip()
                if id_list_tmp not in migrating_id_list:
                    migrating_id_list.append(id_list_tmp)
                    migrating_atoms_list[id_list_tmp] = []
                    migrating_elems_list[id_list_tmp] = []
                migrating_atoms_list[id_list_tmp].append((atom_id1_tmp, atom_id2_tmp))
                migrating_elems_list[id_list_tmp].append(elem_diff_tmp)
            except Exception as e:
                print(f"  Error parsing row: {row}")
                print(f"    Columns 'id', 'atom_id1', 'atom_id2', and 'elem_diff' are required.")
                print(e)
                sys.exit()

    print(f"    Total number of paths: {len(migrating_id_list)}")
    print(f"    Paths:")
    for i1 in range(len(migrating_id_list)):
        str1 = f"{migrating_id_list[i1]:04d}: "
        for i2 in range(len(migrating_atoms_list[migrating_id_list[i1]])):
            atom_id1_tmp = migrating_atoms_list[migrating_id_list[i1]][i2][0]
            atom_id2_tmp = migrating_atoms_list[migrating_id_list[i1]][i2][1]
            e1 = symbols0[atom_id1_tmp-1]
            e2 = symbols0[atom_id2_tmp-1]
            if e1 == "Rn":
                e1 = "Vac"
            if e2 == "Rn":
                e2 = "Vac"
            str1 += f"{migrating_elems_list[migrating_id_list[i1]][i2]}("
            str1 += f"{atom_id1_tmp}[{e1}]->"
            str1 += f"{atom_id2_tmp}[{e2}]" 
            str1 += ")"
            if i2 < len(migrating_atoms_list[migrating_id_list[i1]]) - 1:
                str1 += ", "
        print(f"      {str1}")
    print("  "+"-"*50)

    print("  Making images for each path:")
    for i1 in range(len(migrating_id_list)):
        migrating_id1 = migrating_id_list[i1]
        migrating_atoms1 = migrating_atoms_list[migrating_id1]
        migrating_elems1 = migrating_elems_list[migrating_id1]
        print(f"    Path: {migrating_id1:04d}")
        folder = f"dpath_images_{migrating_id1:04d}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            print(f"      Folder {folder} already exists. Overwriting.")
        os.chdir(folder)

        at3_init = []
        at3_final = []
        for at3 in migrating_atoms1:
            at3_init.append(at3[0])
            at3_final.append(at3[1])
        at4_initonly = []
        at4_finalonly = []
        for at3 in at3_init:
            if at3 not in at3_final:
                at4_initonly.append(at3)
        for at3 in at3_final:
            if at3 not in at3_init:
                at4_finalonly.append(at3)

        num_migrating_atoms = len(at3_init+at4_finalonly)
        coords_init = []
        symbols_init = []
        coords_init_mig = num_migrating_atoms*[None]
        symbols_init_mig = num_migrating_atoms*[None]
        coords_final = []
        symbols_final = []
        coords_final_mig = num_migrating_atoms*[None]
        symbols_final_mig = num_migrating_atoms*[None]
        for ip2 in range(len(coords0)):
            atom_id2_tmp = ip2+1
            if atom_id2_tmp in at3_init:
                nidx = at3_init.index(atom_id2_tmp)
                migrating_elems1_tmp = migrating_elems1[nidx]
                symbols_init_mig[nidx] = migrating_elems1_tmp
                coords_init_mig[nidx] = coords0[ip2]
            elif atom_id2_tmp in at4_finalonly:
                nidx = at4_finalonly.index(atom_id2_tmp)+len(at3_init)
                symbols_init_mig[nidx] = "Rn"
                coords_init_mig[nidx] = coords0[ip2]
            else:
                symbols_init.append(symbols0[ip2])
                coords_init.append(coords0[ip2])
            if atom_id2_tmp in at3_final:
                nidx = at3_final.index(atom_id2_tmp)
                migrating_elems1_tmp = migrating_elems1[nidx]
                symbols_final_mig[nidx] = migrating_elems1_tmp
                coords_final_mig[nidx] = coords0[ip2]
            elif atom_id2_tmp in at4_initonly:
                nidx = at4_initonly.index(atom_id2_tmp)+len(at3_final)
                symbols_final_mig[nidx] = "Rn"
                coords_final_mig[nidx] = coords0[ip2]
            else:
                symbols_final.append(symbols0[ip2])
                coords_final.append(coords0[ip2])   

        print(f"    Initial coordinates:")
        for i1,c1 in zip(symbols_init_mig, coords_init_mig):
            print(f"      {i1}: {c1}")
        print(f"    Final coordinates:")
        for i1,c1 in zip(symbols_final_mig, coords_final_mig):
            print(f"      {i1}: {c1}")

        symbols_init = symbols_init + symbols_init_mig
        coords_init = coords_init + coords_init_mig
        symbols_final = symbols_final + symbols_final_mig
        coords_final = coords_final + coords_final_mig
        symbols_init2 = []
        coords_init2 = []
        symbols_final2 = []
        coords_final2 = []
        ncnt_init = 0
        ncnt_final = 0
        for i2 in range(len(symbols_init)):
            if "Rn" not in symbols_init[i2]:
                symbols_init2.append(symbols_init[i2])
                coords_init2.append(coords_init[i2])
                if symbols_init[i2] == "F":
                    ncnt_init += 1
            if "Rn" not in symbols_final[i2]:
                symbols_final2.append(symbols_final[i2])
                coords_final2.append(coords_final[i2])
                if symbols_final[i2] == "F":
                    ncnt_final += 1

        structure_init = {
            "cell": latt_const0,
            "elements": symbols_init2,
            "coords": coords_init2,
        }
        out_poscar_path_init = os.path.join("POSCAR_init.vasp")
        output_vasp(out_poscar_path_init, structure_init, coords_are_cartesian=False)
        print(f"      Outputting the initial structure to {out_poscar_path_init}")
        structure_final = {
            "cell": latt_const0,
            "elements": symbols_final2,
            "coords": coords_final2,
        }
        out_poscar_path_final = os.path.join("POSCAR_final.vasp")
        output_vasp(out_poscar_path_final, structure_final, coords_are_cartesian=False)
        print(f"      Outputting the final structure to {out_poscar_path_final}")

        sys.argv = [
            "pydecs-dpath-mkimages-twoPOSCARs",
            out_poscar_path_init,
            out_poscar_path_final,
            "-n",str(n_images),
            "-t",str(tol_diff),
            "-o",filename_outcomb,
            # "-i",
            ]
        print(f"    Running pydecs-dpath-mkimages-twoPOSCARs")
        mkimages_from_twoposcars()
        print("  "+"-"*50)
        os.chdir("../")


if __name__ == "__main__":
    print("test")
    search_diffpath_long()

