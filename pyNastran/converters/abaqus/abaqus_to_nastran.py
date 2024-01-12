from __future__ import annotations
import os
import sys
from collections import defaultdict
from typing import TYPE_CHECKING

import numpy as np

from pyNastran.utils.numpy_utils import integer_types # , float_types
from pyNastran.bdf.bdf import BDF, CaseControlDeck, Subcase
from pyNastran.converters.abaqus.abaqus import (
    Abaqus, Step, read_abaqus, get_nodes_nnodes_nelements)
if TYPE_CHECKING:
    from cpylog import SimpleLogger

def _add_part_to_nastran(nastran_model: BDF, elements, pid: int,
                         nid_offset: int, eid_offset: int) -> int:
    log = nastran_model.log

    log.debug('starting part...')
    element_types = {etype: eids_nids
                     for etype, eids_nids in elements.element_types.items()
                     if eids_nids[0] is not None}

    unstacked_eids = [eids_nodes[0] for eids_nodes in element_types.values()]
    all_eids = np.hstack(unstacked_eids)
    ueids = np.unique(all_eids)
    map_eids = (len(all_eids) != len(ueids))
    abaqus_type_to_etype = {
        'b31h': 'CBEAM',
        's3': 'CTRIA3',
        's3r': 'CTRIA3',
        'cpe3': 'CTRIA3',
        'cpe3r': 'CTRIA3',

        's4': 'CQUAD4',
        's4r': 'CQUAD4',
        'cpe4': 'CQUAD4',
        'cpe4r': 'CQUAD4',

        'c3d4': 'CTETRA',
        'c3d4r': 'CTETRA',
        'c3d10': 'CTETRA',
        'c3d10r': 'CTETRA',
        'c3d10h': 'CTETRA',

        'c3d6': 'CPENTA',
        'c3d15': 'CPENTA',
        'c3d6r': 'CPENTA',
        'c3d15r': 'CPENTA',

        'c3d8': 'CHEXA',
        'c3d20': 'CHEXA',
        'c3d8r': 'CHEXA',
        'c3d20r': 'CHEXA',

        'cohax4': None,
        'coh2d4': None,
        'cax3': None,
        'cax4r': None,
        'r2d2': None,
    }

    type_eid_map_to_eid = {}
    for etype, eids_nids in element_types.items():
        eids_, part_nids = eids_nids
        if eids_ is None and part_nids is None:
            continue

        # TODO: well that's annoying...abaqus can have duplicate ids
        #if eid_offset:
        #eids = (eid_offset + 1 - eids_.min()) + eids_
        if map_eids:
            nastran_etype = abaqus_type_to_etype[etype]
            eids = eid_offset + np.arange(len(eids_)) + 1
            for eid1, eid2 in zip(eids_, eids):
                type_eid_map_to_eid[(nastran_etype, eid1)] = eid2
        else:
            eids = eids_


        #print(f'eids[{etype} = {eids}; eid_offset={eid_offset}')
        log.warning(f'writing etype={etype} eids={eids_}->{eids}')
        if nid_offset > 0:
            # don't use += or it's an inplace operation
            part_nids = part_nids + nid_offset

        if etype == 'r2d2':
            log.warning('skipping r2d2; should this be a RBE1/RBAR?')
            continue

        if etype == 'b31h':
            for eid, nids in zip(eids, part_nids):
                x = None
                g0 = nids[2]
                nids = [nids[0], nids[1]]
                nastran_model.add_cbeam(
                    eid, pid, nids, x, g0, offt='GGG', bit=None,
                    pa=0, pb=0, wa=None, wb=None, sa=0, sb=0, comment='')
        elif etype in {'s3', 's3r', 'cpe3', 'cpe3r'}:
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_ctria3(eid, pid, nids, theta_mcid=0.0, zoffset=0., tflag=0,
                                         T1=None, T2=None, T3=None, comment='')
        elif etype in {'s4', 's4r', 'cpe4', 'cpe4r'}:
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_cquad4(eid, pid, nids, theta_mcid=0.0, zoffset=0., tflag=0,
                                         T1=None, T2=None, T3=None, T4=None, comment='')
        elif etype in {'s8', 's8r'}:
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_cquad8(eid, pid, nids, theta_mcid=0.0, zoffset=0., tflag=0,
                                         T1=None, T2=None, T3=None, T4=None, comment='')
        elif etype in {'c3d4', 'c3d4r'}: # , 'c3d10', 'c3d10r', 'c3d10h'}:
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_ctetra(eid, pid, nids, comment='')
        elif etype in {'c3d10', 'c3d10r', 'c3d10h'}:
            quadratic_tetra
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_ctetra(eid, pid, nids, comment='')
        elif etype in {'c3d6', 'c3d6r'}:
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_cpenta(eid, pid, nids, comment='')
        elif etype in {'c3d15', 'c3d15r'}:
            quadratic_penta
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_cpenta(eid, pid, nids, comment='')
        elif etype in {'c3d8', 'c3d8r'}:
            for eid, nids in zip(eids, part_nids):
                nastran_model.add_chexa(eid, pid, nids, comment='')
        elif etype in {'c3d20', 'c3d20r'}:
            for eid, nids in zip(eids, part_nids):
                # the last 8 nodes are flipped in sets of 2
                (n1, n2, n3, n4,
                 n5, n6, n7, n8,
                 n9, n10, n11, n12,
                 n13, n14, n15, n16,
                 n17, n18, n19, n20) = nids
                nids2 = [
                    n1, n2, n3, n4,
                    n5, n6, n7, n8,
                    n9, n10, n11, n12,

                    n17, n18, n19, n20,
                    n13, n14, n15, n16,]
                nastran_model.add_chexa(eid, pid, nids2, comment='')
        elif etype in {'cohax4', 'coh2d4', 'cax3', 'cax4r'}:
            del eids, part_nids
            log.warning(f'skipping etype={etype!r}')
            continue
        else:
            raise NotImplementedError(etype)
        eid_offset += len(eids)
        del eids, part_nids
        #print(etype, eid_offset)

    #add_lines(grid, nidsi, part.r2d2, nid_offset)

    #add_tris(grid, nidsi, part.cps3, nid_offset)
    #add_tris(grid, nidsi, part.cpe3, nid_offset)

    #add_quads(grid, nidsi, part.cpe4, nid_offset)
    #add_quads(grid, nidsi, part.cpe4r, nid_offset)

    #add_quads(grid, nidsi, part.cps4, nid_offset)
    #add_quads(grid, nidsi, part.cps4r, nid_offset)

    #add_quads(grid, nidsi, part.coh2d4, nid_offset)
    #add_quads(grid, nidsi, part.cohax4, nid_offset)

    #add_tris(grid, nidsi, part.cax3, nid_offset)
    #add_quads(grid, nidsi, part.cax4, nid_offset)
    #add_quads(grid, nidsi, part.cax4r, nid_offset)

    ## solids
    #add_tetras(grid, nidsi, part.c3d10h, nid_offset)
    #add_hexas(grid, nidsi, part.c3d8r, nid_offset)
    assert eid_offset > 0, eid_offset
    return eid_offset


def _create_nastran_nodes_elements(model: Abaqus, nastran_model: BDF) -> None:
    log = model.log
    nid_offset = 0
    eid_offset = 0

    pid = 1
    if model.nids is not None and len(model.nids):
        nnodesi = model.nodes.shape[0]
        elements = model.elements
        eid_offset = _add_part_to_nastran(nastran_model, elements, pid, nid_offset, eid_offset)
        nid_offset += nnodesi

    eid_offset = 0
    for unused_part_name, part in model.parts.items():
        log.warning(f'part_name = {unused_part_name!r} eid_offset={eid_offset:d}')
        nnodesi = part.nodes.shape[0]
        #nidsi = part.nids

        elements = part.elements
        eid_offset = _add_part_to_nastran(nastran_model, elements, pid, nid_offset, eid_offset)
        #nids.append(nidsi)
        assert eid_offset > 0, eid_offset
        nid_offset += nnodesi
        for shell_section in part.shell_sections:
            log.info('shell')
        for shell_section in part.shell_sections:
            log.info('solid')
    #nids = np.hstack(nids)

    pid = 1
    mid = 1
    for solid_section in model.solid_sections:
        #print(solid_section)
        mat_name = solid_section.material_name
        mat = model.materials[mat_name]
        element_set = solid_section.elset
        log.warning(f'element_set = {element_set}')
        #print(mat)
        nastran_model.add_psolid(pid, mid, cordm=0,
                                 integ=None, stress=None, isop=None, fctn='SMECH', comment='')
        _create_mat1(nastran_model, mat, mid)

        log.info('solid section')
        mid += 1

    for shell_section in model.shell_sections:
        #print(shell_section)
        mat_name = shell_section.material_name
        mat = model.materials[mat_name]
        #print(mat)
        t = shell_section.thickness
        nastran_model.add_pshell(pid, mid1=mid, t=t, mid2=mid, twelveIt3=1.0, mid3=None, tst=0.833333,
                                 nsm=0.0, z1=None, z2=None, mid4=None, comment='')
        _create_mat1(nastran_model, mat, mid)

        log.info('shell section')
        mid += 1

def _create_mat1(nastran_model: BDF, mat, mid: int):
    G = None
    rho = 0.0
    tref = None
    alpha = None

    sections = mat.sections
    elastic = sections['elastic']
    E = elastic[0]
    nu = elastic[1]
    if 'density' in sections:
        densities = sections['density']
        rho = densities[0]
    if 'expansion' in sections:
        tref, alpha = sections['expansion']
    nastran_model.add_mat1(mid, E, G, nu, rho=rho, a=alpha, tref=tref,
                           ge=0.0, St=0.0, Sc=0.0, Ss=0.0, mcsid=0, comment='')

def abaqus_to_nastran_filename(abaqus_inp_filename: str,
                               nastran_filename_out: str,
                               size: int=8,
                               encoding: Optional[str]=None,
                               log: Optional[SimpleLogger]=None) -> BDF:
    if isinstance(abaqus_inp_filename, Abaqus):
        model = abaqus_inp_filename
    else:
        model = read_abaqus(abaqus_inp_filename, encoding=encoding, log=log, debug=True)
    log = model.log

    nnodes, nids, nodes, nelements = get_nodes_nnodes_nelements(
        model, stop_for_no_elements=True)
    assert nnodes > 0, nnodes
    assert nelements > 0, nelements

    nastran_model = BDF(debug=True, log=log, mode='msc')
    nastran_model.add_param('POST', -1, comment='')
    for nid, xyz in zip(nids, nodes):
        nastran_model.add_grid(nid, xyz)
    _create_nastran_nodes_elements(model, nastran_model)
    #for step in model.steps:
        #print(step)

    _create_nastran_loads(model, nastran_model)
    try:
        str(nastran_model.case_control_deck)
    except AssertionError:
        log.error('No case control deck found...skipping')
        #print(f'{nastran_model.case_control_deck}')
        nastran_model.case_control_deck = None
    nastran_model.write_bdf(
        nastran_filename_out, size=size,
        encoding=None,
        #nodes_size=None, elements_size=None,
        #loads_size=None, is_double=False, interspersed=False,
        enddata=True, write_header=True, close=True)
    x = 1
    return nastran_model

def _write_boundary_as_nastran(model: Abaqus,
                               step: Abaqus,
                               nastran_model: BDF,
                               case_control_deck: CaseControlDeck) -> None:
    if not step.boundaries:
        return
    for iboundary, boundary in enumerate(step.boundaries):
        fixed_spcs = defaultdict(list)
        for (nid, dof), value in boundary.nid_dof_to_value.items():
            nids = _get_nodes(model, nid)
            #assert isinstance(nid, int), nid
            for nid in nids:
                if value == 0.0:
                    fixed_spcs[dof].append(nid)
                else:
                    raise RuntimeError((nid, dof, value))

        subcase_id = iboundary + 1
        spc_id = iboundary + 1
        subcase = case_control_deck.create_new_subcase(subcase_id)
        subcase.add('SPC', spc_id, [], 'STRESS-type')
        for dof, nids in fixed_spcs.items():
            #  spc_id: int, components: str, nodes
            nastran_model.add_spc1(spc_id, str(dof), nids)

def _create_nastran_loads(model: Abaqus, nastran_model: BDF):
    log = nastran_model.log
    if nastran_model.case_control_deck is None:
        nastran_model.case_control_deck = CaseControlDeck([], log=nastran_model.log)

    case_control_deck = nastran_model.case_control_deck
    _write_boundary_as_nastran(model, model, nastran_model, case_control_deck)

    output_map = {
        'U': 'DISP',
        'RF': 'SPCFORCE',  # Reaction Force
        'S': 'STRESS',
        'E': 'STRAIN',
        'ENER': 'ESE',
        #'NOD': disables the error estimator; nastran doesn't have one :)
        #'NOE': disables the error estimator; nastran doesn't have one :)
    }
    for istep, step in enumerate(model.steps):
        subcase_id = istep + 1
        load_id = subcase_id
        if subcase_id in nastran_model.subcases:
            subcase = nastran_model.subcases[subcase_id]
        else:
            subcase = case_control_deck.create_new_subcase(subcase_id)

        _write_boundary_as_nastran(model, step, nastran_model, case_control_deck)
        for output in step.node_output + step.element_output:
            output_upper = output.upper()
            if output_upper in {'NOD', 'NOE'}:
                log.warning(f'skipping output request={output}')
                continue

            try:
                base_output = output_map[output_upper]
            except KeyError:
                raise KeyError(f'output={output!r} is not in [u, rf, s, e, ener]')
            subcase.add(base_output, 'ALL', ['PRINT', 'PLOT'], 'STRESS-type')

        _write_distributed_loads(model, step, nastran_model, subcase, load_id)
        _write_concentrated_loads(model, step, nastran_model, subcase, load_id)

def _write_concentrated_loads(model: Abaqus,
                              step: Step,
                              nastran_model: BDF, subcase: Subcase,
                              load_id: int) -> None:
    def fxyz():
        return np.zeros(3, dtype='float32')

    for cload in step.cloads:
        assert nastran_model.sol is None or nastran_model.sol == 101, nastran_model.sol
        nastran_model.sol = 101
        subcase.add('LOAD', load_id, [], 'STRESS-type')
        #subcase['LOAD'] = load_id
        forces = defaultdict(fxyz)
        moments = defaultdict(fxyz)
        for cloadi in cload:
            nid, dof, mag = cloadi
            nids = _get_nodes(model, nid)
            assert dof in [1, 2, 3], cload

            for nid in nids:
                if dof in {1, 2, 3}:
                    forces[nid][dof - 1] = mag
                elif dof in {4, 5, 6}:
                    moments[nid][dof - 4] = mag
                else:
                    raise NotImplementedError(cloadi)

        mag = 1.0
        if len(forces):
            for nid, xyz in forces.items():
                assert isinstance(nid, integer_types), nid
                nastran_model.add_force(load_id, nid, mag, xyz, cid=0, comment='')
        if len(moments):
            for nid, xyz in moments.items():
                assert isinstance(nid, integer_types), nid
                nastran_model.add_moment(load_id, nid, mag, xyz, cid=0, comment='')

        #print(step.cloads)
    #step.cloads

def _write_distributed_loads(model: Abaqus,
                             step: Step,
                             nastran_model: BDF, subcase: Subcase,
                             load_id: int) -> None:
    for dload in step.dloads:
        assert nastran_model.sol is None or nastran_model.sol == 101, nastran_model.sol
        nastran_model.sol = 101
        subcase.add('LOAD', load_id, [], 'STRESS-type')
        #pressures = []
        for dloadi in dload:
            eid, tag = dloadi[:2]
            if tag in {'P1', 'P2', 'P3', 'P4', 'P5', 'P6'}:
                face = tag
                assert len(dloadi) == 3, dloadi
                mag = dloadi[-1]
                eids = _get_elements(model, eid)
                pressure = mag

                if isinstance(face, str):
                    assert face[0] == 'P' and len(face) == 2, face
                    chexa_face_map = {
                        # take the first and 3rd nodes
                        1: (1-1, 3-1),  #face 1: 1-2-3-4
                        2: (5-1, 7-1),  #face 2: 5-8-7-6
                        3: (1-1, 6-1),  #face 3: 1-5-6-2
                        4: (2-1, 7-1),  #face 4: 2-6-7-3
                        5: (3-1, 8-1),  #face 5: 3-7-8-4
                        6: (4-1, 5-1),  #face 6: 4-8-5-1
                        # subtract 1 to make it 0 based
                    }
                    pressures = [pressure, None, None, None]
                    face_int = int(face[-1])
                    for eid in eids:
                        element = nastran_model.elements[eid]
                        if element.type == 'CHEXA':
                            i1, i3 = chexa_face_map[face_int]
                            n1 = element.nodes[i1]
                            n3 = element.nodes[i3]
                            nastran_model.add_pload4(
                                load_id, [eid], pressures, g1=n1, g34=n3, cid=0, nvector=None,
                                surf_or_line='SURF', line_load_dir='NORM', comment='')
                        else:
                            raise NotImplementedError(element)
                else:
                    for eid in eids:
                        asfd
                        nastran_model.add_pload2(load_id, pressure, [eid], comment='')
                        #nastran_model.add_pload(load_id, pressure, nodes, comment='')

            elif tag == 'GRAV':
                assert len(dloadi) == 6, dloadi
                mag, gx, gy, gz = dloadi[2:]
                N = [gx, gy, gz]
                nastran_model.add_grav(load_id, mag, N, cid=0, mb=0, comment='')
            else:
                raise RuntimeError(dloadi)

def _get_nodes(model: Abaqus, nid: Union[int, str]) -> list[int]:
    if isinstance(nid, integer_types):
        nids = [nid]
    else:
        nids = model.node_sets[nid.lower()]
    return nids

def _get_elements(model: Abaqus, eid: Union[int, str]) -> list[int]:
    if isinstance(eid, integer_types):
        eids = [eid]
    else:
        eids = model.element_sets[eid.lower()]
    return eids

def cmd_abaqus_to_nastran(argv=None, log: Optional[SimpleLogger]=None,
                          quiet: str=False) -> None:
    """Interface for abaqus_to_nastran"""
    if argv is None:
        argv = sys.argv

    default_encoding = sys.getdefaultencoding()
    msg = (
        'Usage:\n'
        '  abaqus_to_nastran ABAQUS_INP_IN [--large] [--encoding ENCODING]\n'
        '  abaqus_to_nastran ABAQUS_INP_IN NASTRAN_BDF_OUT [--large] [--encoding ENCODING]\n'
        '  abaqus_to_nastran -h | --help\n'
        '  abaqus_to_nastran -v | --version\n'
        '\n'
        'Required Arguments:\n'
        '  ABAQUS_INP_IN       path to abaqus.inp file\n'
        '  NASTRAN_BDF_OUT     path to nastran.bdf file (default=abaqus.bdf)\n'
        '\n'

        'Nastran Options:\n'
        '  --large             writes the data in large field format\n'
        '\n'

        'Abaqus Options:\n' # 'utf8bom' = 'utf-8-sig'
        f'  -encoding ENCODING  Specify the encoding (e.g., latin1, cp1252, utf8, utf-8-sig); default={default_encoding!s}\n'
        '\n'

        'Info:\n'
        '  -h, --help     show this help message and exit\n'
        "  -v, --version  show program's version number and exit\n"
        '\n'
        'Examples:\n'
        '  # creates model.bdf\n'
        '  abaqus_to_nastran model.inp\n\n'
        '  # creates fem.bdf\n'
        '  abaqus_to_nastran model.inp fem.bdf\n\n'
        '  # creates model.bdf with large field format\n'
        '  abaqus_to_nastran model.inp --large\n\n'
        '  # creates model.bdf an alternate encoding\n'
        '  abaqus_to_nastran model.inp --encoding utf-8-sig\n\n'
        '\n'
    )
    from docopt import docopt
    import pyNastran
    ver = str(pyNastran.__version__)
    data = docopt(msg, version=ver, argv=argv[1:])

    encoding = default_encoding
    if data['ENCODING']:
        encoding = data['ENCODING']
    if not quiet:  # pragma: no cover
        print(data)
    abaqus_inp_filename = data['ABAQUS_INP_IN']
    nastran_filename_out = os.path.splitext(abaqus_inp_filename)[0] + '.bdf'

    if log is None:
        level = 'warning' if quiet else 'debug'
        from cpylog import SimpleLogger
        log = SimpleLogger(level=level)

    if data['NASTRAN_BDF_OUT']:
        nastran_filename_out = data['NASTRAN_BDF_OUT']
    else:
        log.info(f"NASTRAN_BDF_OUT wasn't specified; using {nastran_filename_out!r}")

    size = 8
    if data['--large']:
        size = 16

    abaqus_to_nastran_filename(abaqus_inp_filename, nastran_filename_out,
                               encoding=encoding, size=size, log=log)

if __name__ == '__main__':
    cmd_abaqus_to_nastran()
