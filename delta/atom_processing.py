from ase.atoms import Atoms

def filter_atoms(atoms, atom_symbol, filter_array):
    positions = atoms.get_positions()
    symbols = atoms.get_chemical_symbols()
    
    new_positions = []
    new_symbols = []
    
    count = 0
    for i, symbol in enumerate(symbols):
        if symbol == atom_symbol:
            if filter_array[count] == 1:
                new_positions.append(positions[i])
                new_symbols.append(symbol)
            count += 1
        else:
            new_positions.append(positions[i])
            new_symbols.append(symbol)
    
    return Atoms(positions=new_positions, symbols=new_symbols, cell=atoms.get_cell(), pbc=atoms.get_pbc())
