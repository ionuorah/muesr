import warnings

from muesr.core.spg import spacegroup_from_data
from muesr.core.parsers import *
#from muesr.core.symmetry import Symmetry
from muesr.core.nprint  import nprint, nprintmsg

have_spg = True

try:
    import spglib as spg
except ImportError:
    try:
        from pyspglib import spglib as spg
    except ImportError:
        nprint("Spg Library not loaded", "warn")
        have_spg = False



        
def symsearch(sample, precision=1e-4):
    """
    Identifies symmetry operations of the unit cell using spglib and 
    update the sample definition.
    
    :param sample: A sample object.
    :param float precision: atoms are assumed equivalent if distances are 
                            smaller than precision. In Angstrom.
    :returns: True if succesful, False otherwise.
    :rtype: bool
    """
    
    if sample._check_lattice() and have_spg:
        dataset = spg.get_symmetry_dataset(sample.cell, symprec=precision)
        sample.sym = spacegroup_from_data(no=dataset['number'],
                                          rotations=dataset['rotations'],
                                          translations=dataset['translations'])
        
        warnings.warn("Warning, information regarding spacegroup setting might be wrong!",RuntimeWarning, stacklevel=0)
        
        return True
    elif not have_spg:
        warnings.warn("Warning, spglib not found. This function will always return False.")
        return False
    else:
        return False
     
