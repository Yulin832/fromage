"""The class used to manipulate lists of Atoms
"""
import numpy as np
# from copy import copy
from copy import deepcopy

from cryspy.utils.atom import Atom
import cryspy.io.edit_file as ef

def try_ismol(to_test):
    """ Raise exception if the argument is not a Mol object"""
    if not isinstance(to_test, Mol):
        raise TypeError("Cannot cast " + type(to_test).__name__ + " and Mol object")

class Mol(object):
    """
    Object representing a list of atoms.

    This class can be used to reflect any number of molecules, point charges or
    unit cells. Although Mol shares many methods with list, it deliberately does
    not inherit it in order to avoid nonsensical operations such as Mol1 > Mol2

    Attributes
    ----------
    atoms : list of Atom objects
        Member atoms of Mol
    min_lap : float
        The minimum distance of two overlapping vdw radii for the atoms to be
        considered bonded
    vectors : 3 x 3 numpy array
        Lattice vectors of the unit cell

    """

    def __init__(self, in_atoms, min_lap=0.6, vectors=np.zeros((3, 3))):
        # In case the user feeds a lone atom:
        if isinstance(in_atoms, Atom):
            in_atoms = [in_atoms]
        self.atoms = in_atoms
        self.min_lap = min_lap
        self.vectors = vectors

    def __repr__(self):
        out_str = ""
        for atom in self.atoms:
            out_str += atom.__str__() + "\n"
        return out_str

    def __str__(self):
        return self.__repr__()

    # list-y behaviour
    def append(self, element):
        self.atoms.append(element)

    def extend(self, other_mol):
        self.atoms.extend(other_mol.atoms)

    def insert(self, i, element):
        self.atoms.insert(i, element)

    def remove(self, element):
        self.atoms.remove(element)

    def pop(self, i=-1):
        return self.atoms.pop(i)

    def clear(self):
        self.atoms.clear()

    def count(self, element):
        return self.atoms.count()

    def __add__(self, other_mol):
        try_ismol(other_mol)
        return Mol(deepcopy(self).atoms + other_mol.atoms, min_lap = self.min_lap, vectors = self.vectors)

    def __len__(self):
        return len(self.atoms)

    def __eq__(self, other):
        return self.atoms == other.atoms

    def __getitem__(self, index):
        return self.atoms[index]

    def __setitem__(self,index,value):
        self.atoms[index] = value

    def write_xyz(self, name):
        """Write an xyz file of the Mol"""
        ef.write_xyz(name, self.atoms)

    def select(self, labels):
        """
        Return a molecule out of the current Mol.

        The function returns a new Mol of selected atoms atoms. The selection is
        done by measuring by how much adjacent vdw spheres overlap. The returned
        Mol's attributes are new objects obtained via a deep copy.

        Parameters
        ----------
        label : int or list of ints
            The number of the atoms from which the molecules are generated.

        Returns
        -------
        selected : Mol object
            The selected molecule
        """

        # Make sure that labels is a list
        if isinstance(labels, int):
            labels = [labels]

        # Check for duplicate labels
        if len(labels) > len(set(labels)):
            raise TypeError("Some labels are repeated")

        selected = Mol(deepcopy([self[i] for i in labels]), min_lap = self.min_lap, vectors = self.vectors)
        remaining = deepcopy(self)
        for atom in selected:
            if atom in remaining:
                remaining.remove(atom)

        old_atoms = deepcopy(selected)

        # While there are atoms to add
        cont = True
        while cont:
            cont = False
            new_atoms = Mol([])
            for old in old_atoms:
                for rem in remaining:
                    if old.at_lap(rem) >= self.min_lap:
                        new_atoms.append(rem)
                        selected.append(rem)
                        remaining.remove(rem)
                        cont = True # An atom was added so continue loop
            old_atoms = new_atoms
        return selected
    # 
    # def per_select(self, labels, old_pos=False):
    #     """
    #     Select a molecule out of a Mol in a periodic system.
    #
    #     Parameters
    #     ----------
    #     label : int or list of ints
    #         The number of the atoms from which the molecules are generated.
    #     old_pos : bool
    #         Option to print the selected molecule at its original coordinates
    #
    #     Returns
    #     -------
    #     selected_img : Mol object
    #         The atoms belonging to the molecule which is selected with certain
    #         atoms translated so that the molecule is fully connected without
    #         periodic boundaries
    #     selected : Mol object
    #         The atoms belonging to the molecule which is selected before
    #         translations
    #
    #     """
    #
    #     # Make sure that labels is a list
    #     if isinstance(labels, int):
    #         labels = [labels]
    #
    #     # Check for duplicate labels
    #     if len(labels) > len(set(labels)):
    #         raise TypeError("Some labels are repeated")
    #
    #     # list of selected atoms from the unit cell
    #     selected = Mol(deepcopy([self[i] for i in labels]), min_lap = self.min_lap, vectors = self.vectors)
    #     # list of selected atoms where the periodic image
    #     # atoms are translated back to form a molecule
    #     selected_img = Mol(deepcopy([self[i] for i in labels]), min_lap = self.min_lap, vectors = self.vectors)
    #
    #     # While there are atoms to add
    #     cont = True
    #     while cont == True:
    #         cont = False
    #         for i in selected_img:
    #             for j in self.atoms:
    #                 # contains the distance from the point or image and the
    #                 # coordinates of the point or image
    #                 gamma = i.dist_lat(j.x, j.y, j.z, vectors[
    #                     0], vectors[1], vectors[2])
    #
    #                 # if the atom is close enough to be part of the molecule
    #                 # and is not already part of the molecule
    #                 if gamma[0] <= max_r and j not in selected:
    #                     selected.append(j)
    #                     k = copy(j)
    #                     k.x, k.y, k.z = gamma[1:]
    #                     selected_img.append(k)
    #                     cont = True # An atom was added so continue loop
    #
    #     return selected, selected_img