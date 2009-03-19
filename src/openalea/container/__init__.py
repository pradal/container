#from _container import *
#from id_dict import IdDict
from utils import IdDict
from graph import Graph
from grid import Grid
from relation import Relation

################################
#
#	topomesh
#
################################
from topomesh import Topomesh
from topomesh_txt import write_topomesh,read_topomesh
from topomesh_algo import clean_geometry,clean_orphans,flip_edge,\
						expand,border,shrink,\
						expand_to_border,expand_to_region,external_border,\
						clean_duplicated_borders,merge_wisps
