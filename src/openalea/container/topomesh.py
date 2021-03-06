"""
This module provide a simple pure python implementation
for a topomesh interface
"""

from array import array
from interface.topomesh import (TopomeshError, InvalidWisp, InvalidDegree,
                                ITopomesh, IWispListMesh, INeighborhoodMesh,
                                IMutableMesh)
from utils import IdDict


class StrInvalidWisp(InvalidWisp):
    """
    exception raised when a wrong wisp id is provided
    """

    def __init__(self, degree, wid):
        msg = "wisp %d of degree %d does not exist" % (wid, degree)
        InvalidWisp.__init__(self, msg)


class StrInvalidDegree(InvalidDegree):
    """
    exception raised when a wrong degree is provided
    """

    def __init__(self, degree):
        msg = "degree %d is outside of mesh bounds" % degree
        InvalidDegree.__init__(self, msg)


class Topomesh(ITopomesh, IWispListMesh, INeighborhoodMesh, IMutableMesh):
    """
    implementation of a topological mesh
    """

    def __init__(self, degree, idgenerator="set"):
        """
        constructor of an empty mesh
        """
        self._degree = degree
        self._borders = [None] + [IdDict(idgenerator=idgenerator) for i in
                                  xrange(degree)]
        self._regions = [IdDict(idgenerator=idgenerator)] + [{} for i in
                                                             xrange(degree - 1)]

    def get_idgenerator_type(self):
        return self._regions[0].get_generator_type()

    def enable_id_reuse(self, enabled=True):
        for border in self._borders:
            if border is not None:
                border.enable_id_reuse(enabled)
        self._regions[0].enable_id_reuse(enabled)

    def id_reuse_enabled(self):
        return self._regions[0].id_reuse_enabled()

    ########################################################################
    #
    #               Mesh concept
    #
    ########################################################################
    def degree(self):
        return self._degree

    degree.__doc__ = ITopomesh.degree.__doc__

    def is_valid(self):
        return True

    is_valid.__doc__ = ITopomesh.is_valid.__doc__

    def has_wisp(self, degree, wid):
        if degree == 0:
            try:
                return wid in self._regions[0]
            except IndexError:
                raise StrInvalidDegree(degree)
        else:
            try:
                return wid in self._borders[degree]
            except IndexError:
                raise StrInvalidDegree(degree)

    has_wisp.__doc__ = ITopomesh.has_wisp.__doc__

    def _iter_borders(self, degree, wid):
        """Internal function to access borders of an element
        """
        return iter(self._borders[degree][wid])

    def _borders_with_offset(self, degree, wids, offset):
        if offset == 0:
            return wids
        else:
            ret = set()
            for wid in wids:
                ret |= set(self._borders_with_offset(degree - 1,
                                                     self._iter_borders(degree,
                                                                        wid),
                                                     offset - 1))
            return iter(ret)

    def borders(self, degree, wid, offset=1):
        if degree - offset < 0:
            raise InvalidDegree("smallest wisps have no borders")
        return self._borders_with_offset(degree, [wid], offset)

    borders.__doc__ = ITopomesh.borders.__doc__

    def nb_borders(self, degree, wid):
        if degree < 1:
            raise InvalidDegree("smallest wisps have no borders")
        return len(self._borders[degree][wid])

    nb_borders.__doc__ = ITopomesh.nb_borders.__doc__

    def _iter_regions(self, degree, wid):
        """Internal function to access regions of an element
        """
        return iter(self._regions[degree][wid])

    def _regions_with_offset(self, degree, wids, offset):
        if offset == 0:
            return wids
        else:
            ret = set()
            for wid in wids:
                ret |= set(self._regions_with_offset(degree + 1,
                                                     self._iter_regions(degree,
                                                                        wid),
                                                     offset - 1))
            return iter(ret)

    def regions(self, degree, wid, offset=1):
        if (degree + offset) > self.degree():
            raise InvalidDegree("biggest wisps do not separate regions")
        return self._regions_with_offset(degree, [wid], offset)

    regions.__doc__ = ITopomesh.regions.__doc__

    def nb_regions(self, degree, wid):
        if degree >= self.degree():
            raise InvalidDegree("biggest wisps do not separate regions")
        return len(self._regions[degree][wid])

    nb_regions.__doc__ = ITopomesh.nb_regions.__doc__

    ########################################################################
    #
    #               Wisp list concept
    #
    ########################################################################
    def wisps(self, degree):
        if degree == 0:
            try:
                return iter(self._regions[degree])
            except IndexError:
                raise StrInvalidDegree(degree)
        else:
            try:
                return iter(self._borders[degree])
            except IndexError:
                raise StrInvalidDegree(degree)

    wisps.__doc__ = IWispListMesh.wisps.__doc__

    def nb_wisps(self, degree):
        if degree == 0:
            try:
                return len(self._regions[degree])
            except IndexError:
                raise StrInvalidDegree(degree)
        else:
            try:
                return len(self._borders[degree])
            except IndexError:
                raise StrInvalidDegree(degree)

    nb_wisps.__doc__ = IWispListMesh.nb_wisps.__doc__

    ########################################################################
    #
    #               Neighborhood concept
    #
    ########################################################################
    def border_neighbors(self, degree, wid):
        for bid in self.borders(degree, wid):
            for rid in self.regions(degree - 1, bid):
                if rid != wid:
                    yield rid

    border_neighbors.__doc__ = INeighborhoodMesh.border_neighbors.__doc__

    def nb_border_neighbors(self, degree, wid):
        return len(list(self.border_neighbors(degree, wid)))

    nb_border_neighbors.__doc__ = INeighborhoodMesh.nb_border_neighbors.__doc__

    def region_neighbors(self, degree, wid):
        for rid in self.regions(degree, wid):
            for bid in self.borders(degree + 1, rid):
                if bid != wid:
                    yield bid

    region_neighbors.__doc__ = INeighborhoodMesh.region_neighbors.__doc__

    def nb_region_neighbors(self, degree, wid):
        return len(list(self.region_neighbors(degree, wid)))

    nb_region_neighbors.__doc__ = INeighborhoodMesh.nb_region_neighbors.__doc__

    ########################################################################
    #
    #               Mutable mesh concept
    #
    ########################################################################
    def add_wisp(self, degree, wid=None):
        if degree > 0:
            wid = self._borders[degree].add(array("L"), wid)
            if degree < self.degree():
                self._regions[degree][wid] = array("L")
        else:
            wid = self._regions[degree].add(array("L"), wid)
        return wid

    add_wisp.__doc__ = IMutableMesh.add_wisp.__doc__

    def remove_wisp(self, degree, wid):
        # remove links
        if degree < self.degree():
            for rid in tuple(self.regions(degree, wid)):
                self.unlink(degree + 1, rid, wid)
        if degree > 0:
            for bid in tuple(self.borders(degree, wid)):
                self.unlink(degree, wid, bid)
        # remove element
        if degree < self.degree():
            del self._regions[degree][wid]
        if degree > 0:
            del self._borders[degree][wid]

    remove_wisp.__doc__ = IMutableMesh.remove_wisp.__doc__

    def link(self, degree, wid, border_id):
        if degree < 1:
            raise InvalidDegree("smallest wisps have no neighbors")
        self._borders[degree][wid].append(border_id)
        self._regions[degree - 1][border_id].append(wid)

    link.__doc__ = IMutableMesh.link.__doc__

    def unlink(self, degree, wid, border_id):
        if degree < 1:
            raise InvalidDegree("smallest wisps have no neighbors")
        self._borders[degree][wid].remove(border_id)
        self._regions[degree - 1][border_id].remove(wid)

    unlink.__doc__ = IMutableMesh.unlink.__doc__
