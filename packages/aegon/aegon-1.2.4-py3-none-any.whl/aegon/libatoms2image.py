import os
import numpy as np
from ase import Atoms
from ase.data import covalent_radii
from ase.data.colors import cpk_colors, jmol_colors
from ase.calculators.singlepoint import SinglePointCalculator
# ------------------------------------------------------------------------------------------
# Visualization parameters
bwd = 0.10                     # Bond thickness
dlv = 0.15                     # Cell edge thickness
sphere_factor = 0.60           # Atom size scale factor
projection = 'orthographic'    # or 'perspective'
reflection = 'reflection 0.0'
reflection_model = 'phong 1.0' # or 'specular'
radio_factor = 1.30            # Bond length scaling factor
tmit = 0.00                    # Transparency (transmit parameter)
color_scheme = 'jmol'          # 'cpk' or 'jmol'

# ------------------------------------------------------------------------------------------
def get_color(Z):
    """Return atomic color according to the selected color scheme."""
    return cpk_colors[Z] if color_scheme == 'cpk' else jmol_colors[Z]
# ------------------------------------------------------------------------------------------
def conventional_visual(atoms, tol=1e-3):
    """Generate a visually complete conventional cell (without deforming it)."""
    if not np.any(atoms.pbc):
        return atoms.copy()
    lattice = atoms.cell.array
    frac_coords = atoms.get_scaled_positions(wrap=False)
    symbols = atoms.get_chemical_symbols()
    new_symbols, new_positions = [], []
    shifts = np.array(np.meshgrid([-1, 0, 1], [-1, 0, 1], [-1, 0, 1])).T.reshape(-1, 3)
    for icoord, sym in zip(frac_coords, symbols):
        for shift in shifts:
            fcoord = icoord + shift
            if np.all((fcoord >= -tol) & (fcoord <= 1.0 + tol)):
                pos = np.dot(fcoord, lattice)
                new_symbols.append(sym)
                new_positions.append(pos)
    return Atoms(symbols=new_symbols, positions=new_positions, cell=lattice, pbc=True)

# ------------------------------------------------------------------------------------------
aspect_ratios_4by3 = {
    'a': (800, 600),
    'b': (1024, 768),
    'c': (1280, 960),
    'd': (1600, 1200),
    'e': (2048, 1536),
    'f': (3200, 2400),
    'g': (6000, 4500),
}

# ------------------------------------------------------------------------------------------
def draw_cell_edge(v1, v2, opnew):
    """Draw a cell edge as a black cylinder."""
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    print(
        f'cylinder {{<{x1:9.6f},{y1:9.6f},{z1:9.6f}> '
        f'<{x2:9.6f},{y2:9.6f},{z2:9.6f}>, {dlv:.4f} '
        f'pigment{{color rgb <0,0,0>}} finish {{{reflection_model} {reflection}}}}}',
        file=opnew
    )

# ------------------------------------------------------------------------------------------
def write_image(atoms, basename, f=1.2, quality='b',
                draw_forces=False, arrow_scale=10.0,
                arrow_thickness=0.05, arrow_color=(0, 0, 0)):
    """Generate a PNG image using POV-Ray, optionally drawing force arrows."""

    width, height = aspect_ratios_4by3.get(quality, (1024, 768))
    name_pov = basename + '.pov'
    name_png = basename + '.png'

    # Retrieve forces safely
    forces = None
    if 'forces' in atoms.arrays:
        forces = atoms.arrays['forces']
    elif atoms.calc is not None:
        try:
            forces = atoms.get_forces()
        except Exception:
            forces = None

    # Open POV-Ray scene file
    with open(name_pov, 'w') as opnew:
        print('global_settings { assumed_gamma 1.0 }', file=opnew)
        print('background { color rgb<2.0, 2.0, 2.0> }', file=opnew)
        print('light_source { <10, -8, -8> color rgb <1,1,1> }', file=opnew)
        print('light_source { <-8, 8, 8> color rgb <1,1,1> }', file=opnew)

        # Draw cell edges if periodic
        if atoms.pbc.any():
            matrix = atoms.cell
            a1, a2, a3 = matrix
            a0 = -(a1 + a2 + a3) / 2
            for pair in [
                (a0, a0 + a1), (a0, a0 + a2), (a0, a0 + a3),
                (a0 + a1, a0 + a1 + a2), (a0 + a1, a0 + a1 + a3),
                (a0 + a2, a0 + a1 + a2), (a0 + a2, a0 + a2 + a3),
                (a0 + a3, a0 + a1 + a3), (a0 + a3, a0 + a2 + a3),
                (a0 + a1 + a2, a0 + a1 + a2 + a3),
                (a0 + a1 + a3, a0 + a1 + a2 + a3),
                (a0 + a2 + a3, a0 + a1 + a2 + a3)
            ]:
                draw_cell_edge(*pair, opnew)
            d = max(np.linalg.norm(v) for v in [a1, a2, a3])
        else:
            ctd = atoms.get_center_of_mass()
            r = [np.linalg.norm(atom.position - ctd) + covalent_radii[atom.number] for atom in atoms]
            d = 2.0 * max(r)

        # Camera
        factor = f * d
        print(f'camera {{{projection} location <0,0,{factor:.2f}> look_at <0,0,0> rotate y*0.0}}\n', file=opnew)

        # Bonds
        nn = len(atoms)
        for i in range(nn):
            ri = covalent_radii[atoms[i].number]
            pos_i = atoms[i].position
            for j in range(i + 1, nn):
                rj = covalent_radii[atoms[j].number]
                pos_j = atoms[j].position
                uij = pos_j - pos_i
                rr = np.linalg.norm(uij)
                if rr == 0:
                    continue
                if rr / (ri + rj) < radio_factor:
                    uijn = uij / rr
                    col_i = get_color(atoms[i].number)
                    col_j = get_color(atoms[j].number)
                    start_i = pos_i + sphere_factor * ri * uijn
                    start_j = pos_j - sphere_factor * rj * uijn
                    mid = (start_i + start_j) / 2
                    for (xa, ya, za, xb, yb, zb, col) in [
                        (start_i[0], start_i[1], start_i[2], mid[0], mid[1], mid[2], col_i),
                        (mid[0], mid[1], mid[2], start_j[0], start_j[1], start_j[2], col_j)
                    ]:
                        kolor = f"<{col[0]:.3f},{col[1]:.3f},{col[2]:.3f}>"
                        print(
                            f'cylinder {{<{xa:9.6f},{ya:9.6f},{za:9.6f}> '
                            f'<{xb:9.6f},{yb:9.6f},{zb:9.6f}>, {bwd:.2f} '
                            f'pigment {{color rgb {kolor} transmit {tmit:.2f}}} '
                            f'finish {{{reflection_model} {reflection}}}}}',
                            file=opnew
                        )

        # Atoms
        for atom in atoms:
            ri = covalent_radii[atom.number]
            cpk = get_color(atom.number)
            xx, yy, zz = atom.position
            kolor = f"<{cpk[0]:.3f},{cpk[1]:.3f},{cpk[2]:.3f}>"
            print(
                f'sphere {{<{xx:9.6f},{yy:9.6f},{zz:9.6f}>, {sphere_factor*ri:6.4f} '
                f'pigment {{color rgb {kolor} transmit {tmit:.2f}}} '
                f'finish {{{reflection_model} {reflection}}}}}',
                file=opnew
            )

        # Force arrows
        if draw_forces and forces is not None:
            try:
                arrow_rgb = f"<{arrow_color[0]:.3f},{arrow_color[1]:.3f},{arrow_color[2]:.3f}>"
                for pos, F in zip(atoms.positions, forces):
                    normF = np.linalg.norm(F)
                    if normF < 1e-6:
                        continue
                    uF = F / normF
                    shaft_length = normF * arrow_scale * 0.85
                    cone_length = normF * arrow_scale * 0.15
                    start = pos
                    end_shaft = pos + uF * shaft_length
                    end_cone = end_shaft + uF * cone_length

                    print(
                        f'cylinder {{<{start[0]:.6f},{start[1]:.6f},{start[2]:.6f}> '
                        f'<{end_shaft[0]:.6f},{end_shaft[1]:.6f},{end_shaft[2]:.6f}>, {arrow_thickness:.3f} '
                        f'pigment{{color rgb {arrow_rgb}}} finish {{{reflection_model}}}}}',
                        file=opnew
                    )
                    print(
                        f'cone {{<{end_shaft[0]:.6f},{end_shaft[1]:.6f},{end_shaft[2]:.6f}>, {arrow_thickness*2:.3f} '
                        f'<{end_cone[0]:.6f},{end_cone[1]:.6f},{end_cone[2]:.6f}>, 0 '
                        f'pigment{{color rgb {arrow_rgb}}} finish {{{reflection_model}}}}}',
                        file=opnew
                    )
            except Exception as e:
                print(f"Could not draw force arrows: {e}")

    os.system(f"povray +A Display=Off Output_File_Type=N Width={width} Height={height} {name_pov} > /dev/null 2>&1")
    os.remove(name_pov)
    #print(f"Output: {name_png}")

# ------------------------------------------------------------------------------------------
def ex4():
    import glob
    from aegon.libcodegaussian import get_geometry_gaussian
    from aegon.libutils import readxyzs, rotate_matrix, align, sort_by_energy
    frames=[]
    for ifile in sorted(glob.glob("*.out")):
        frame=get_geometry_gaussian(ifile)
        frames.extend([frame])
    frames=sort_by_energy(frames, opt=1)
    #traj='stage2.xyz'
    #frames = readxyzs(traj)
    for i, frame in enumerate(frames, start=1):
        basename = f"frame{i:03d}"
        #rotate_matrix(frame, matrix)
        align(frame)
        write_image(frame, basename, f=1.0, quality='f', draw_forces=False)
# ------------------------------------------------------------------------------------------
#ex4()
