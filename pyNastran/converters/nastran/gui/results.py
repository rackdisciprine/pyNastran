from copy import deepcopy
import numpy as np

from pyNastran.gui.gui_objects.displacements import Table


class LayeredTableResults(Table):
    def __init__(self, subcase_id, headers, eids, eid_max, scalars,
                 methods,
                 data_formats=None,
                 nlabels=None, labelsize=None, ncolors=None, colormap='jet',
                 set_max_min=False, uname='Geometry'):
        """this is a centroidal result

        Parameters
        ----------
        headers : List[str]
            the sidebar word
        titles : List[str]
            the legend title

        """
        location = 'centroid'
        titles = None
        Table.__init__(
            self, subcase_id, location, titles, headers, scalars,
            data_formats=data_formats, nlabels=nlabels,
            labelsize=labelsize, ncolors=ncolors,
            colormap=colormap, set_max_min=set_max_min,
            uname=uname)
        self.methods = methods
        self.eids = eids
        self.eid_max = eid_max

    def finalize(self):
        self.titles_default = deepcopy(self.titles)
        self.headers_default = deepcopy(self.headers)

    def get_methods(self, i):
        return self.methods

    def deflects(self, unused_i, unused_res_name):
        return False

    def get_default_title(self, i, name):
        """legend title"""
        (itime, ilayer, imethod, unused_header) = name
        return self.methods[imethod]

    def get_title(self, i, name):
        """legend title"""
        (itime, ilayer, imethod, unused_header) = name
        return self.methods[imethod]

    def get_header(self, i, name):
        """a header shows up in the text"""
        (itime, ilayer, imethod, header) = name
        return self.methods[imethod] + ': ' + header

    def get_data_format(self, i, name):
        return '%.3f'  # TODO: update
    def get_default_data_format(self, i, name):
        return '%.3f'  # TODO: update
    def get_scale(self, i, name):
        return None
    def get_default_scale(self, i, name):
        return None

    def get_scalar(self, i, name):
        return self.get_result(i, name)

    def get_magnitude(self, i, name):
        scalar = self.get_scalar(i, name)  # TODO: update
        mag = scalar
        if scalar.dtype.name in ['complex64']:
            mag = np.sqrt(scalar.real ** 2 + scalar.imag ** 2)
        return mag

    def get_min_max(self, i, name):
        mag = self.get_magnitude(i, name)
        return np.nanmin(mag), np.nanmax(mag)

    def get_default_min_max(self, i, name):
        mag = self.get_magnitude(i, name)
        return np.nanmin(mag), np.nanmax(mag)

    def get_result(self, i, name):
        (itime, ilayer, imethod, unused_header) = name
        scalars = self.scalars[itime, :, ilayer, imethod]

        if len(scalars) == self.eid_max:
            return scalars
        data = np.full(self.eid_max, np.nan, dtype=scalars.dtype)
        #print(f'data.shape={data.shape} eids.shape={self.eids.shape} scalars.shape={scalars.shape}')
        #print(self.methods)
        data[self.eids] = scalars
        return data


class SimpleTableResults(Table):
    def __init__(self, subcase_id, headers, eids, eid_max, scalars,
                 methods,
                 data_format=None,
                 nlabels=None, labelsize=None, ncolors=None, colormap='jet',
                 location='centroid',
                 set_max_min=False, uname='Geometry'):
        """this is a centroidal result

        Parameters
        ----------
        headers : List[str]
            the sidebar word
        titles : List[str]
            the legend title

        """
        titles = None
        assert data_format is not None, data_format
        ntimes = scalars.shape[0]
        data_formats = [data_format] * len(methods) * ntimes
        Table.__init__(
            self, subcase_id, location, titles, headers, scalars,
            data_formats=data_formats, nlabels=nlabels,
            labelsize=labelsize, ncolors=ncolors,
            colormap=colormap, set_max_min=set_max_min,
            uname=uname)
        self.methods = methods
        self.eids = eids
        self.eid_max = eid_max
        assert len(eids) == scalars.shape[1], f'len(eids)={len(eids)} scalars.shape={scalars.shape}'

    def finalize(self):
        self.titles_default = deepcopy(self.titles)
        self.headers_default = deepcopy(self.headers)

    def get_methods(self, i):
        return self.methods

    #def deflects(self, unused_i, unused_res_name):
        #return False

    def get_default_title(self, i, name):
        """legend title"""
        (itime, imethod, unused_header) = name
        return self.methods[imethod]

    def get_title(self, i, name):
        """legend title"""
        (itime, imethod, unused_header) = name
        return self.methods[imethod]

    def get_header(self, i, name):
        """a header shows up in the text"""
        (itime, imethod, header) = name
        return self.methods[imethod] + ': ' + header

    #def get_data_format(self, i, name):
        #return '%.3f'  # TODO: update
    #def get_default_data_format(self, i, name):
        #return '%.3f'  # TODO: update
    def get_scale(self, i, name):
        return None
    def get_default_scale(self, i, name):
        return None

    def get_scalar(self, i, name):
        return self.get_result(i, name)

    def get_magnitude(self, i, name):
        scalar = self.get_scalar(i, name)  # TODO: update
        mag = scalar
        if scalar.dtype.name in ['complex64']:
            mag = np.sqrt(scalar.real ** 2 + scalar.imag ** 2)
        return mag

    def get_min_max(self, i, name):
        mag = self.get_magnitude(i, name)
        return np.nanmin(mag), np.nanmax(mag)

    def get_default_min_max(self, i, name):
        mag = self.get_magnitude(i, name)
        return np.nanmin(mag), np.nanmax(mag)

    def get_result(self, i, name):
        #print(i, name)
        (itime, imethod, unused_header) = name
        scalars = self.scalars[itime, :, imethod]

        if len(scalars) == self.eid_max:
            return scalars
        data = np.full(self.eid_max, np.nan, dtype=scalars.dtype)
        #print(f'data.shape={data.shape} eids.shape={self.eids.shape} scalars.shape={scalars.shape}')
        #print(self.methods)
        try:
            data[self.eids] = scalars
        except IndexError:
            raise RuntimeError(f'{self.uname!r} eids.max()={self.eids.max()} scalars.shape={scalars.shape}')
        return data

    def get_data_format(self, i, name):
        try:
            return self.data_formats[i]
        except IndexError:
            print(f'data_formats = {self.data_formats}')
            print(str(self))
            print("ires =", i)
            print(name)
            raise
