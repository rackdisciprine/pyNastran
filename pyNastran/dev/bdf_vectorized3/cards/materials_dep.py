from __future__ import annotations
from itertools import zip_longest
from typing import Optional, TYPE_CHECKING
import numpy as np
#from pyNastran.bdf.field_writer_8 import print_card_8 # , print_float_8, print_field_8
#from pyNastran.bdf.field_writer_16 import print_card_16, print_scientific_16, print_field_16
#from pyNastran.bdf.field_writer_double import print_scientific_double
from pyNastran.bdf.bdf_interface.assign_type import (
    string, integer, double,
    integer_or_blank, double_or_blank, string_or_blank,
)
#from pyNastran.bdf.cards.materials import mat1_E_G_nu, get_G_default, set_blank_if_default

from pyNastran.dev.bdf_vectorized3.cards.base_card import Material, get_print_card_8_16, parse_material_check
from pyNastran.dev.bdf_vectorized3.cards.write_utils import get_print_card, array_str, array_default_int, array_float, array_float_nan

if TYPE_CHECKING:  # pragma: no cover
    from pyNastran.bdf.bdf_interface.bdf_card import BDFCard
    from pyNastran.dev.bdf_vectorized3.bdf import BDF
    from pyNastran.dev.bdf_vectorized3.types import TextIOLike


class MATT1(Material):
    """
    Specifies temperature-dependent material properties on MAT1 entry
    fields via TABLEMi entries.

    +-------+-------+-------+-------+-------+--------+------+------+-------+
    |   1   |   2   |   3   |   4   |   5   |    6   |  7   |  8   |   9   |
    +=======+=======+=======+=======+=======+========+======+======+=======+
    | MATT1 |  MID  |  T(E) |  T(G) | T(NU) | T(RHO) | T(A) |      | T(GE) |
    +-------+-------+-------+-------+-------+--------+------+------+-------+
    |       | T(ST) | T(SC) | T(SS) |       |        |      |      |       |
    +-------+-------+-------+-------+-------+--------+------+------+-------+

    """
    @Material.clear_check
    def clear(self) -> None:
        self.material_id = np.array([], dtype='int32')
        self.e_table = np.array([], dtype='int32')
        self.g_table = np.array([], dtype='int32')
        self.nu_table = np.array([], dtype='int32')
        self.rho_table = np.array([], dtype='int32')
        self.alpha_table = np.array([], dtype='int32')
        self.ge_table = np.array([], dtype='int32')
        self.st_table = np.array([], dtype='int32')
        self.sc_table = np.array([], dtype='int32')
        self.ss_table = np.array([], dtype='int32')

    def add(self, mid, e_table=None, g_table=None, nu_table=None, rho_table=None,
            a_table=None, ge_table=None, st_table=None, sc_table=None, ss_table=None,
            comment: str='') -> int:
        """Creates a MATT1 card"""
        self.cards.append((mid, e_table, g_table, nu_table, rho_table, a_table,
                           ge_table, st_table, sc_table, ss_table, comment))
        self.n += 1
        return self.n

    def add_card(self, card: BDFCard, comment: str='') -> int:
        """
        Adds a MATT1 card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        mid = integer(card, 1, 'mid')
        e_table = integer_or_blank(card, 2, 'T(E)')
        g_table = integer_or_blank(card, 3, 'T(G)')
        nu_table = integer_or_blank(card, 4, 'T(nu)')
        rho_table = integer_or_blank(card, 5, 'T(rho)')
        a_table = integer_or_blank(card, 6, 'T(A)')
        ge_table = integer_or_blank(card, 8, 'T(ge)')
        st_table = integer_or_blank(card, 9, 'T(st)')
        sc_table = integer_or_blank(card, 10, 'T(sc)')
        ss_table = integer_or_blank(card, 11, 'T(ss)')

        assert len(card) <= 12, f'len(MATT1 card) = {len(card):d}\ncard={card}'
        #return MATT1(mid, e_table, g_table, nu_table, rho_table, a_table,
                     #ge_table, st_table, sc_table, ss_table, comment=comment)
        self.cards.append((mid, e_table, g_table, nu_table, rho_table, a_table,
                           ge_table, st_table, sc_table, ss_table, comment))
        self.n += 1
        return self.n

    @Material.parse_cards_check
    def parse_cards(self) -> None:
        ncards = len(self.cards)
        material_id = np.zeros(ncards, dtype='int32')
        e_table = np.zeros(ncards, dtype='int32')
        g_table = np.zeros(ncards, dtype='int32')
        nu_table = np.zeros(ncards, dtype='int32')
        rho_table = np.zeros(ncards, dtype='int32')
        alpha_table = np.zeros(ncards, dtype='int32')
        ge_table = np.zeros(ncards, dtype='int32')
        st_table = np.zeros(ncards, dtype='int32')
        sc_table = np.zeros(ncards, dtype='int32')
        ss_table = np.zeros(ncards, dtype='int32')

        for i, card in enumerate(self.cards):
            (mid, e_tablei, g_tablei, nu_tablei, rho_tablei, a_tablei,
             ge_tablei, st_tablei, sc_tablei, ss_tablei, comment) = card
            e_tablei = 0 if e_tablei is None else e_tablei
            g_tablei = 0 if g_tablei is None else g_tablei
            nu_tablei = 0 if nu_tablei is None else nu_tablei
            rho_tablei = 0 if rho_tablei is None else rho_tablei
            a_tablei = 0 if a_tablei is None else a_tablei
            ge_tablei = 0 if ge_tablei is None else ge_tablei
            st_tablei = 0 if st_tablei is None else st_tablei
            sc_tablei = 0 if sc_tablei is None else sc_tablei
            ss_tablei = 0 if ss_tablei is None else ss_tablei
            material_id[i] = mid
            e_table[i] = e_tablei
            g_table[i] = g_tablei
            nu_table[i] = nu_tablei
            rho_table[i] = rho_tablei
            alpha_table[i] = a_tablei
            ge_table[i] = ge_tablei
            st_table[i] = st_tablei
            sc_table[i] = sc_tablei
            ss_table[i] = ss_tablei
        self._save(material_id, e_table, g_table, nu_table,
                   rho_table, alpha_table,
                   ge_table,
                   st_table, sc_table, ss_table,)
        self.sort()
        self.cards = []

    def _save(self, material_id, e_table, g_table, nu_table,
              rho_table, alpha_table,
              ge_table,
              st_table, sc_table, ss_table,):
        if len(self.material_id):
            asdf
            #material_id = np.hstack([self.material_id, material_id])
            #E = np.hstack([self.E, E])
            #G = np.hstack([self.G, G])
            #nu = np.hstack([self.nu, nu])
            #rho = np.hstack([self.rho, rho])
            #alpha = np.hstack([self.alpha, alpha])
            #tref = np.hstack([self.tref, tref])
            #ge = np.hstack([self.ge, ge])
            #Ss = np.hstack([self.Ss, Ss])
            #St = np.hstack([self.St, St])
            #Sc = np.hstack([self.Sc, Sc])
        self.material_id = material_id
        self.e_table = e_table
        self.g_table = g_table
        self.nu_table = nu_table
        self.rho_table = rho_table
        self.alpha_table = alpha_table
        self.ge_table = ge_table
        self.st_table = st_table
        self.sc_table = sc_table
        self.ss_table = ss_table

    def set_used(self, used_dict: dict[str, list[np.ndarray]]) -> None:
        table0 = np.hstack([
            self.e_table, self.g_table, self.nu_table,
            self.rho_table, self.alpha_table,
            self.ge_table, self.st_table, self.ss_table, ])
        utable0 = np.unique(table0)
        table = np.setdiff1d(utable0, [0])
        used_dict['tablem_id'].append(table)

    def convert(self, stiffness_scale: float=1.0,
                density_scale: float=1.0,
                alpha_scale: float=1.0,
                temperature_scale: float=1.0,
                stress_scale: float=1.0, **kwargs) -> None:
        pass
        tables0 = [
            (self.e_table, stiffness_scale),
            (self.g_table, stiffness_scale),
            (self.rho_table, density_scale),
            # nu - nope
            (self.alpha_table, alpha_scale),
            (self.st_table, stress_scale),
            (self.sc_table, stress_scale),
            (self.ss_table, stress_scale),
        ]
        table_ids = {}
        for table0, scale in tables0:
            utable0 = np.unique(table0)
            table = np.setdiff1d(utable0, [0])
            #if table:
                #table_ids[scale].append(table)
            #model.tablem

    def __apply_slice__(self, mat: MATT1, i: np.ndarray) -> None:  # ignore[override]
        mat.n = len(i)
        mat.material_id = self.material_id[i]
        mat.e_table = self.e_table[i]
        mat.g_table = self.g_table[i]
        mat.nu_table = self.nu_table[i]
        mat.rho_table = self.rho_table[i]
        mat.alpha_table = self.alpha_table[i]
        mat.ge_table = self.ge_table[i]
        mat.st_table = self.st_table[i]
        mat.sc_table = self.sc_table[i]
        mat.ss_table = self.ss_table[i]

    def geom_check(self, missing: dict[str, np.ndarray]):
        pass

    @parse_material_check
    def write_file(self, bdf_file: TextIOLike,
                   size: int=8, is_double: bool=False,
                   write_card_header: bool=False) -> None:
        max_int = self.material_id.max()
        print_card = get_print_card(size, max_int)

        material_id = array_str(self.material_id, size=size)
        e_table = array_default_int(self.e_table, default=0, size=size)
        g_table = array_default_int(self.g_table, default=0, size=size)
        nu_table = array_default_int(self.nu_table, default=0, size=size)
        rho_table = array_default_int(self.rho_table, default=0, size=size)
        alpha_table = array_default_int(self.alpha_table, default=0, size=size)
        ge_table = array_default_int(self.ge_table, default=0, size=size)
        ss_table = array_default_int(self.ss_table, default=0, size=size)
        st_table = array_default_int(self.st_table, default=0, size=size)
        sc_table = array_default_int(self.sc_table, default=0, size=size)

        #tables = np.column_stack([self.e_table, self.g_table, self.nu_table, self.rho_table])
        for mid, e, g, nu, rho, alpha, ge, ss, st, sc, \
            in zip_longest(material_id, e_table, g_table, nu_table, rho_table,
                           alpha_table, ge_table,
                           ss_table, st_table, sc_table):
            list_fields = ['MATT1', mid, e, g, nu, rho, alpha, '', ge,
                           st, sc, ss]
            bdf_file.write(print_card(list_fields))
        return

class MATS1(Material):
    """
    Specifies stress-dependent material properties for use in applications
    involving nonlinear materials. This entry is used if a MAT1, MAT2 or MAT9
    entry is specified with the same MID in a nonlinear solution sequence
    (SOLs 106 and 129).

    #: Identification number of a MAT1, MAT2, or MAT9 entry.
    self.mid = mid

    #: Identification number of a TABLES1 or TABLEST entry. If H is
    #: given, then this field must be blank.
    self.tid = tid

    #: Type of material nonlinearity. ('NLELAST' for nonlinear elastic
    #: or 'PLASTIC' for elastoplastic.)
    self.Type = Type

    #: Work hardening slope (slope of stress versus plastic strain)
    #: in units of stress. For elastic-perfectly plastic cases,
    #: H=0.0.  For more than a single slope in the plastic range,
    #: the stress-strain data must be supplied on a TABLES1 entry
    #: referenced by TID, and this field must be blank
    self.h = h

    #: Hardening Rule, selected by one of the following values
    #: (Integer): (1) Isotropic (Default) (2) Kinematic
    #: (3) Combined isotropic and kinematic hardening
    self.hr = hr

    #: Yield function criterion, selected by one of the following
    #: values (1) Von Mises (2) Tresca (3) Mohr-Coulomb
    #: (4) Drucker-Prager
    self.yf = yf
    #: Initial yield point
    self.limit1 = limit1
    #: Internal friction angle, measured in degrees, for the
    #: Mohr-Coulomb and Drucker-Prager yield criteria
    self.limit2 = limit2
        if self.Type not in ['NLELAST', 'PLASTIC', 'PLSTRN']:
            raise ValueError('MATS1 Type must be [NLELAST, PLASTIC, PLSTRN]; Type=%r' % self.Type)

    """
    @Material.clear_check
    def clear(self) -> None:
        self.material_id = np.array([], dtype='int32')

    def add(self, mid: int, tid: int, Type: str,
            h: float, hr: int, yf: int, limit1: float, limit2: float,
            stress_strain_measure: str='', comment: str='') -> int:
        """Creates a MATS1 card"""
        assert isinstance(Type, str), f'Type={Type!r}'
        self.cards.append((mid, tid, Type, h, hr, yf, limit1, limit2, stress_strain_measure, comment))
        self.n += 1
        return self.n

    def add_card(self, card: BDFCard, comment: str='') -> int:
        """
        Adds a MATS1 card from ``BDF.add_card(...)``

        Parameters
        ----------
        card : BDFCard()
            a BDFCard object
        comment : str; default=''
            a comment for the card

        """
        mid = integer(card, 1, 'mid')
        tid = integer_or_blank(card, 2, 'tid')
        Type = string(card, 3, 'Type')

        if Type not in {'NLELAST', 'PLASTIC', 'PLSTRN'}:
            raise ValueError('MATS1 Type must be [NLELAST, PLASTIC, PLSTRN]; Type=%r' % Type)
        if Type == 'NLELAST':
            # should we even read these?
            h = None
            hr = None
            yf = None
            limit1 = None
            limit2 = None
            #h = blank(card, 4, 'h')
            #hr = blank(card, 6, 'hr')
            #yf = blank(card, 5, 'yf')
            #limit1 = blank(card, 7, 'yf')
            #limit2 = blank(card, 8, 'yf')
        else:
            h = double_or_blank(card, 4, 'H')
            yf = integer_or_blank(card, 5, 'yf', default=1)
            hr = integer_or_blank(card, 6, 'hr', default=1)
            limit1 = double(card, 7, 'limit1')

            if yf in [3, 4]:
                limit2 = double(card, 8, 'limit2')
            else:
                #limit2 = blank(card, 8, 'limit2')
                limit2 = None
        stress_strain_measure = string_or_blank(card, 10, 'stress/strain measure', default='')
        assert len(card) <= 9, f'len(MATS1 card) = {len(card):d}\ncard={card}'
        #return MATS1(mid, tid, Type, h, hr, yf, limit1, limit2, comment=comment)
        self.cards.append((mid, tid, Type, h, hr, yf, limit1, limit2, stress_strain_measure, comment))
        self.n += 1
        return self.n

    @Material.parse_cards_check
    def parse_cards(self) -> None:
        ncards = len(self.cards)
        material_id = np.zeros(ncards, dtype='int32')
        table_id = np.zeros(ncards, dtype='int32')
        Type = np.zeros(ncards, dtype='|U8')
        h = np.zeros(ncards, dtype='float64')
        hr = np.zeros(ncards, dtype='int32')
        yf = np.zeros(ncards, dtype='int32')
        limit1 = np.zeros(ncards, dtype='float64')
        limit2 = np.zeros(ncards, dtype='float64')
        stress_strain_measure = np.zeros(ncards, dtype='|U8')

        for i, card in enumerate(self.cards):
            (mid, tid, typei, hi, hri, yfi, limit1i, limit2i, stress_strain_measurei, comment) = card
            tid = 0 if tid is None else tid
            hri = 1 if hri is None else hri
            yfi = 1 if yfi is None else yfi
            material_id[i] = mid
            table_id[i] = tid
            Type[i] = typei
            h[i] = hi
            hr[i] = hri
            yf[i] = yfi
            limit1[i] = limit1i
            limit2[i] = limit2i
            stress_strain_measure[i] = stress_strain_measurei
        self._save(material_id, table_id, Type, h, hr, yf, limit1, limit2, stress_strain_measure)
        self.sort()
        self.cards = []

    def _save(self, material_id, table_id, Type, h, hr, yf, limit1, limit2, stress_strain_measure):
        if len(self.material_id):
            asdf
            #material_id = np.hstack([self.material_id, material_id])
            #E = np.hstack([self.E, E])
        self.material_id = material_id
        self.table_id = table_id
        self.Type = Type
        self.h = h
        self.hr = hr
        self.yf = yf
        self.limit1 = limit1
        self.limit2 = limit2
        self.stress_strain_measure = stress_strain_measure

    def set_used(self, used_dict: dict[str, list[np.ndarray]]) -> None:
        pass
        #table0 = np.hstack([
            #self.e_table, self.g_table, self.nu_table,
            #self.rho_table, self.alpha_table,
            #self.ge_table, self.st_table, self.ss_table, ])
        #utable0 = np.unique(table0)
        #table = np.setdiff1d(utable0, [0])
        #used_dict['tablem_id'].append(table)

    #def convert(self, stiffness_scale: float=1.0,
                #density_scale: float=1.0,
                #alpha_scale: float=1.0,
                #temperature_scale: float=1.0,
                #stress_scale: float=1.0, **kwargs) -> None:
        #tables0 = [
            #(self.e_table, stiffness_scale),
            #(self.g_table, stiffness_scale),
            #(self.rho_table, density_scale),
            ## nu - nope
            #(self.alpha_table, alpha_scale),
            #(self.st_table, stress_scale),
            #(self.sc_table, stress_scale),
            #(self.ss_table, stress_scale),
        #]
        #table_ids = {}
        #for table0, scale in tables0:
            #utable0 = np.unique(table0)
            #table = np.setdiff1d(utable0, [0])
            #if table:
                #table_ids[scale].append(table)
            #model.tablem

    def __apply_slice__(self, mat: MATT1, i: np.ndarray) -> None:  # ignore[override]
        mat.n = len(i)
        mat.material_id = self.material_id[i]
        mat.table_id = self.table_id[i]
        mat.Type = self.Type[i]
        mat.h = self.h[i]
        mat.hr = self.hr[i]
        mat.yf = self.yf[i]
        mat.limit1 = self.limit1[i]
        mat.limit2 = self.limit2[i]
        mat.stress_strain_measure = self.stress_strain_measure[i]

    def geom_check(self, missing: dict[str, np.ndarray]):
        pass

    @property
    def max_id(self):
        return max(self.material_id.max(), self.table_id.max())

    @parse_material_check
    def write_file(self, bdf_file: TextIOLike,
                   size: int=8, is_double: bool=False,
                   write_card_header: bool=False) -> None:
        print_card = get_print_card(size, self.max_id)

        material_id = array_str(self.material_id, size=size)
        table_id = array_str(self.table_id, size=size)
        h = array_str(self.h, size=size)
        yf = array_str(self.yf, size=size)
        hr = array_str(self.hr, size=size)
        limit1 = array_float(self.limit1, size=size)
        limit2 = array_float_nan(self.limit2, size=size)

        #tables = np.column_stack([self.e_table, self.g_table, self.nu_table, self.rho_table])
        for mid, table_idi, typei, hi, yfi, hri, limit1i, limit2i, stress_strain_measure \
            in zip_longest(material_id, table_id, self.Type,
                           h, yf, hr, limit1, limit2, self.stress_strain_measure):
            list_fields = ['MATS1', mid, table_idi, typei,
                           hi, yfi, hri, limit1i, limit2i, stress_strain_measure]
            bdf_file.write(print_card(list_fields))
        return
