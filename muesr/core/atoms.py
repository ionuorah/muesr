# Copyright (C) 2011 Atsushi Togo
# All rights reserved.
#
# This file is part of phonopy.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# * Neither the name of the phonopy project nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np

class Atoms:
    """
    Atoms class compatible with the ASE Atoms class
    Only stuff needed by muesr is implemented.
    
    >>> a = 4.05  # Gold lattice constant
    >>> b = a / 2
    >>> fcc = Atoms('Au',
    ...             cell=[(0, b, b), (b, 0, b), (b, b, 0)],
    ...             pbc=True)
    
    """
    
    def __init__(self,
                 symbols=None,
                 positions=None,
                 numbers=None, 
                 masses=None,
                 magmoms=None,
                 scaled_positions=None,
                 cell=None,
                 pbc=None):

        # cell
        if cell is None:
            raise ValueError('Only periodic system allowed. Please specify unit cell.')
        else:
            self.cell = np.array(cell, dtype=float)

        # position
        self.scaled_positions = None

        if (not self.cell is None) and  (not positions is None):
            self.set_positions(positions)

        if (not scaled_positions is None):
            self.set_scaled_positions(scaled_positions)

        # Atom symbols
        self.symbols = symbols

        # Atomic numbers
        if numbers is None:
            self.numbers = None
        else:
            self.numbers = np.array(numbers, dtype=int)

        # masses
        self.set_masses(masses)


        # (initial) magnetic moments
        self.set_magnetic_moments(magmoms)


        # number --> symbol
        if not self.numbers is None:
            self.numbers_to_symbols()

        # symbol --> number
        elif not self.symbols is None:
            self.symbols_to_numbers()

        # symbol --> mass
        if self.symbols and (self.masses is None):
            self.symbols_to_masses()

    # Add an atom
    # return atom index
    def extend(self,
                 symbol=None,
                 position=None,
                 number=None, 
                 mass=None,
                 magmom=None,
                 scaled_position=None):
        """
        Extends the current atomic structure by one atom.
        """

        # position

        if (not self.cell is None) and  (not position is None):
            # append scaled position to positions
            self.scaled_positions = np.concatenate(self.scaled_positions, np.dot(position,
                                        np.linalg.inv(self.cell)))
        if (not scaled_position is None):
            #print ((self.scaled_positions, np.array([scaled_position])))
            self.scaled_positions = np.concatenate((self.scaled_positions, np.array([scaled_position])))

        if symbol is None and number is None:
            raise ValueError

        # Atom symbols
        if symbol is None:
            symbol = atom_data[number][1]
        
        self.symbols.append(symbol)

        # Atomic numbers
        if number is None:
            number = symbol_map[symbol]
        
        self.numbers = np.append(self.numbers, number)

        
        # (initial) magnetic moments
        if not (self.magmoms is None):
            if magmom is None:
                magmom = np.array([0,0,0])
            self.magmoms = np.concatenate((self.magmoms, [magmom]))


        # symbol --> mass
        if mass is None:
            mass = atom_data[number][3]
        
        self.masses = np.append(self.masses,mass)
        
        return -1 # stands for last item!

    def del_atom(self, i):
        """
        Removes one atom
        """
        if isinstance(i, int):
            natoms = len(self)
            if i < -natoms or i >= natoms:
                raise IndexError('Index out of range.')
            if not self.magmoms is None:
                self.magmoms      = np.delete(self.magmoms, i, 0)         

            self.symbols.pop(i)  #        = np.delete(self.symbols, i)
            self.numbers          = np.delete(self.numbers, i)
            self.scaled_positions = np.delete(self.scaled_positions, i,0) # axis is needed for scaled pos
            self.masses           = np.delete(self.masses, i)

    def edit_atom(self, i, symbol = None, number = None, magmom = None, mass = None):
        if isinstance(i, int):
            natoms = len(self)
            if i < -natoms or i >= natoms:
                raise IndexError('Index out of range.')
            
            if symbol is None and number  is None:
                raise ValueError

            # Atom symbols
            if symbol is None:
                symbol = atom_data[number][1]
            
            self.symbols[i] = symbol
    
            # Atomic numbers
            if number is None:
                number = symbol_map[symbol]
            
            self.numbers[i] = number
    
            
            # (initial) magnetic moments
            if not (self.magmoms is  None):
                if magmom is None:
                    magmom = np.array([0,0,0])
                self.magmoms[i] = magmom
    
            # symbol --> mass
            if mass is None:
                mass = atom_data[number][3]
            
            self.masses[i] = mass
            
            

    def set_cell(self, cell):
        """
        Set lattice vectors parameters.
        
        :param cell: numpy array of the form
                     [[v1(1), v1(2), v1(3)],
                       v2(1), v2(2), v2(3)],
                       v3(1), v3(2), v3(3)]]
                     where v1, v2, v3 are the lattice vectors.  
        """

        self.cell = np.array(cell, dtype=float)

    def get_cell(self):
        return self.cell.copy()

    def set_positions(self, cart_positions):
        self.scaled_positions = np.dot(cart_positions,
                                        np.linalg.inv(self.cell))

    def get_positions(self):
        return np.dot(self.scaled_positions, self.cell)

    def set_scaled_positions(self, scaled_positions):
        self.scaled_positions = np.array(scaled_positions, dtype=float)

    def get_scaled_positions(self):
        return self.scaled_positions.copy()

    def set_masses(self, masses):
        if masses is None:
            self.masses = None
        else:
            self.masses = np.array(masses, dtype=float)

    def get_masses(self):
        return self.masses.copy()

    def set_magnetic_moments(self, magmoms=None):
        if magmoms is None:
            self.magmoms = None
        else:
            self.magmoms = np.array(magmoms, dtype=float)



    def get_magnetic_moments(self):
        """
        Get magnetic moments if set. None if nothing set.
        """
        if self.magmoms is None:
            return None
        else:
            return self.magmoms.copy()

    

    def set_chemical_symbols(self, symbols):
        self.symbols = symbols

    def get_chemical_symbols(self):
        return self.symbols[:]

    def get_number_of_atoms(self):
        return len(self.scaled_positions)

    def get_atomic_numbers(self):
        return self.numbers.copy()

    def numbers_to_symbols(self):
        self.symbols = [atom_data[n][1] for n in self.numbers]
        
    def symbols_to_numbers(self):
        self.numbers = np.array([symbol_map[s.title()]
                                 for s in self.symbols])
        
    def symbols_to_masses(self):
        self.masses = np.array([atom_data[symbol_map[s.title()]][3]
                                for s in self.symbols])

    def get_volume(self):
        return np.linalg.det(self.cell)

    def __len__(self):
        return len(self.scaled_positions)

    def __getitem__(self, i):
        """
        Return an atom
        """
        if isinstance(i, int):
            natoms = len(self)
            if i < -natoms or i >= natoms:
                raise IndexError('Index out of range.')
            mom = np.array([0,0,0])
            if not self.magmoms is None:
                mom = self.magmoms[i]
            return (self.symbols[i], self.numbers[i], self.scaled_positions[i], mom)

        

atom_data = [ 
    [  0, "mu", "mu", 0.2], # 0
    [  1, "H", "Hydrogen", 1.00794], # 1
    [  2, "He", "Helium", 4.002602], # 2
    [  3, "Li", "Lithium", 6.941], # 3
    [  4, "Be", "Beryllium", 9.012182], # 4
    [  5, "B", "Boron", 10.811], # 5
    [  6, "C", "Carbon", 12.0107], # 6
    [  7, "N", "Nitrogen", 14.0067], # 7
    [  8, "O", "Oxygen", 15.9994], # 8
    [  9, "F", "Fluorine", 18.9984032], # 9
    [ 10, "Ne", "Neon", 20.1797], # 10
    [ 11, "Na", "Sodium", 22.98976928], # 11
    [ 12, "Mg", "Magnesium", 24.3050], # 12
    [ 13, "Al", "Aluminium", 26.9815386], # 13
    [ 14, "Si", "Silicon", 28.0855], # 14
    [ 15, "P", "Phosphorus", 30.973762], # 15
    [ 16, "S", "Sulfur", 32.065], # 16
    [ 17, "Cl", "Chlorine", 35.453], # 17
    [ 18, "Ar", "Argon", 39.948], # 18
    [ 19, "K", "Potassium", 39.0983], # 19
    [ 20, "Ca", "Calcium", 40.078], # 20
    [ 21, "Sc", "Scandium", 44.955912], # 21
    [ 22, "Ti", "Titanium", 47.867], # 22
    [ 23, "V", "Vanadium", 50.9415], # 23
    [ 24, "Cr", "Chromium", 51.9961], # 24
    [ 25, "Mn", "Manganese", 54.938045], # 25
    [ 26, "Fe", "Iron", 55.845], # 26
    [ 27, "Co", "Cobalt", 58.933195], # 27
    [ 28, "Ni", "Nickel", 58.6934], # 28
    [ 29, "Cu", "Copper", 63.546], # 29
    [ 30, "Zn", "Zinc", 65.38], # 30
    [ 31, "Ga", "Gallium", 69.723], # 31
    [ 32, "Ge", "Germanium", 72.64], # 32
    [ 33, "As", "Arsenic", 74.92160], # 33
    [ 34, "Se", "Selenium", 78.96], # 34
    [ 35, "Br", "Bromine", 79.904], # 35
    [ 36, "Kr", "Krypton", 83.798], # 36
    [ 37, "Rb", "Rubidium", 85.4678], # 37
    [ 38, "Sr", "Strontium", 87.62], # 38
    [ 39, "Y", "Yttrium", 88.90585], # 39
    [ 40, "Zr", "Zirconium", 91.224], # 40
    [ 41, "Nb", "Niobium", 92.90638], # 41
    [ 42, "Mo", "Molybdenum", 95.96], # 42
    [ 43, "Tc", "Technetium", 0], # 43
    [ 44, "Ru", "Ruthenium", 101.07], # 44
    [ 45, "Rh", "Rhodium", 102.90550], # 45
    [ 46, "Pd", "Palladium", 106.42], # 46
    [ 47, "Ag", "Silver", 107.8682], # 47
    [ 48, "Cd", "Cadmium", 112.411], # 48
    [ 49, "In", "Indium", 114.818], # 49
    [ 50, "Sn", "Tin", 118.710], # 50
    [ 51, "Sb", "Antimony", 121.760], # 51
    [ 52, "Te", "Tellurium", 127.60], # 52
    [ 53, "I", "Iodine", 126.90447], # 53
    [ 54, "Xe", "Xenon", 131.293], # 54
    [ 55, "Cs", "Caesium", 132.9054519], # 55
    [ 56, "Ba", "Barium", 137.327], # 56
    [ 57, "La", "Lanthanum", 138.90547], # 57
    [ 58, "Ce", "Cerium", 140.116], # 58
    [ 59, "Pr", "Praseodymium", 140.90765], # 59
    [ 60, "Nd", "Neodymium", 144.242], # 60
    [ 61, "Pm", "Promethium", 0], # 61
    [ 62, "Sm", "Samarium", 150.36], # 62
    [ 63, "Eu", "Europium", 151.964], # 63
    [ 64, "Gd", "Gadolinium", 157.25], # 64
    [ 65, "Tb", "Terbium", 158.92535], # 65
    [ 66, "Dy", "Dysprosium", 162.500], # 66
    [ 67, "Ho", "Holmium", 164.93032], # 67
    [ 68, "Er", "Erbium", 167.259], # 68
    [ 69, "Tm", "Thulium", 168.93421], # 69
    [ 70, "Yb", "Ytterbium", 173.054], # 70
    [ 71, "Lu", "Lutetium", 174.9668], # 71
    [ 72, "Hf", "Hafnium", 178.49], # 72
    [ 73, "Ta", "Tantalum", 180.94788], # 73
    [ 74, "W", "Tungsten", 183.84], # 74
    [ 75, "Re", "Rhenium", 186.207], # 75
    [ 76, "Os", "Osmium", 190.23], # 76
    [ 77, "Ir", "Iridium", 192.217], # 77
    [ 78, "Pt", "Platinum", 195.084], # 78
    [ 79, "Au", "Gold", 196.966569], # 79
    [ 80, "Hg", "Mercury", 200.59], # 80
    [ 81, "Tl", "Thallium", 204.3833], # 81
    [ 82, "Pb", "Lead", 207.2], # 82
    [ 83, "Bi", "Bismuth", 208.98040], # 83
    [ 84, "Po", "Polonium", 0], # 84
    [ 85, "At", "Astatine", 0], # 85
    [ 86, "Rn", "Radon", 0], # 86
    [ 87, "Fr", "Francium", 0], # 87
    [ 88, "Ra", "Radium", 0], # 88
    [ 89, "Ac", "Actinium", 0], # 89
    [ 90, "Th", "Thorium", 232.03806], # 90
    [ 91, "Pa", "Protactinium", 231.03588], # 91
    [ 92, "U", "Uranium", 238.02891], # 92
    [ 93, "Np", "Neptunium", 0], # 93
    [ 94, "Pu", "Plutonium", 0], # 94
    [ 95, "Am", "Americium", 0], # 95
    [ 96, "Cm", "Curium", 0], # 96
    [ 97, "Bk", "Berkelium", 0], # 97
    [ 98, "Cf", "Californium", 0], # 98
    [ 99, "Es", "Einsteinium", 0], # 99
    [100, "Fm", "Fermium", 0], # 100
    [101, "Md", "Mendelevium", 0], # 101
    [102, "No", "Nobelium", 0], # 102
    [103, "Lr", "Lawrencium", 0], # 103
    [104, "Rf", "Rutherfordium", 0], # 104
    [105, "Db", "Dubnium", 0], # 105
    [106, "Sg", "Seaborgium", 0], # 106
    [107, "Bh", "Bohrium", 0], # 107
    [108, "Hs", "Hassium", 0], # 108
    [109, "Mt", "Meitnerium", 0], # 109
    [110, "Ds", "Darmstadtium", 0], # 110
    [111, "Rg", "Roentgenium", 0], # 111
    [112, "Cn", "Copernicium", 0], # 112
    [113, "Uut", "Ununtrium", 0], # 113
    [114, "Uuq", "Ununquadium", 0], # 114
    [115, "Uup", "Ununpentium", 0], # 115
    [116, "Uuh", "Ununhexium", 0], # 116
    [117, "Uus", "Ununseptium", 0], # 117
    [118, "Uuo", "Ununoctium", 0], # 118
    ]

symbol_map = {
    "H":1,
    "He":2,
    "Li":3,
    "Be":4,
    "B":5,
    "C":6,
    "N":7,
    "O":8,
    "F":9,
    "Ne":10,
    "Na":11,
    "Mg":12,
    "Al":13,
    "Si":14,
    "P":15,
    "S":16,
    "Cl":17,
    "Ar":18,
    "K":19,
    "Ca":20,
    "Sc":21,
    "Ti":22,
    "V":23,
    "Cr":24,
    "Mn":25,
    "Fe":26,
    "Co":27,
    "Ni":28,
    "Cu":29,
    "Zn":30,
    "Ga":31,
    "Ge":32,
    "As":33,
    "Se":34,
    "Br":35,
    "Kr":36,
    "Rb":37,
    "Sr":38,
    "Y":39,
    "Zr":40,
    "Nb":41,
    "Mo":42,
    "Tc":43,
    "Ru":44,
    "Rh":45,
    "Pd":46,
    "Ag":47,
    "Cd":48,
    "In":49,
    "Sn":50,
    "Sb":51,
    "Te":52,
    "I":53,
    "Xe":54,
    "Cs":55,
    "Ba":56,
    "La":57,
    "Ce":58,
    "Pr":59,
    "Nd":60,
    "Pm":61,
    "Sm":62,
    "Eu":63,
    "Gd":64,
    "Tb":65,
    "Dy":66,
    "Ho":67,
    "Er":68,
    "Tm":69,
    "Yb":70,
    "Lu":71,
    "Hf":72,
    "Ta":73,
    "W":74,
    "Re":75,
    "Os":76,
    "Ir":77,
    "Pt":78,
    "Au":79,
    "Hg":80,
    "Tl":81,
    "Pb":82,
    "Bi":83,
    "Po":84,
    "At":85,
    "Rn":86,
    "Fr":87,
    "Ra":88,
    "Ac":89,
    "Th":90,
    "Pa":91,
    "U":92,
    "Np":93,
    "Pu":94,
    "Am":95,
    "Cm":96,
    "Bk":97,
    "Cf":98,
    "Es":99,
    "Fm":100,
    "Md":101,
    "No":102,
    "Lr":103,
    "Rf":104,
    "Db":105,
    "Sg":106,
    "Bh":107,
    "Hs":108,
    "Mt":109,
    "Ds":110,
    "Rg":111,
    "Cn":112,
    "Uut":113,
    "Uuq":114,
    "Uup":115,
    "Uuh":116,
    "Uus":117,
    "Uuo":118,
    "mu":0,
    }

