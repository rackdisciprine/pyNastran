#import sys
#from numpy import array,cross,dot
from numpy import array
#from numpy.linalg import norm

# my code
from baseCard import BaseCard

class Node(BaseCard): # base class
    def __init__(self,card):
        pass
    def crossReference(self,mesh):
        raise Exception('%s hasnt implemented a crossReference method' %(self.type))
    def __repr__(self):
        raise Exception('%s hasnt implemented a __repr__ method' %(self.type))

class SPOINT(Node):
    """
    SPOINT ID1 ID2 ID3 ID4 ID5 ID6 ID7 ID8
    or
    SPOINT ID1 THRU ID2
    SPOINT 5   THRU 649
    """
    type = 'SPOINT'
    def __init__(self,card):
        Node.__init__(self,card)
        fields  = card.fields(1)
        nFields = card.nFields()
        
        self.spoints = []
        self.dof = '23456'  # the constrained DOF
        i = 0
        while i<nFields: # =1 ???
            if fields[i]=='THRU':
                self.spoints += [fields[i-1],fields[i]+1]
                i+=1
            else:
                self.spoints.append(fields[i])
            i+=1
        ###

    def Position(self):
        return array(0.,0.,0.)

    def __repr__(self):
        ## @todo support THRU in output
        fields = ['SPOINT']+self.spoints
        return self.printCard(fields)
        

class GRDSET(Node):
    """
    Defines default options for fields 3, 7, 8, and 9 of all GRID entries.
    """
    type = 'GRDSET'
    def __init__(self,card):
        ## Grid point coordinate system
        self.cid  = card.field(2,0)
        
        ## Analysis coordinate system
        self.cd   = card.field(6,0)
        
        ## Default SPC constraint on undefined nodes
        self.ps   = card.field(7,0)
        
        ## Superelement ID
        self.seid = card.field(8,0)

    def __repr__(self):
        cid  = self.setBlankIfDefault(self.cid, 0)
        cd   = self.setBlankIfDefault(self.cd,  0)
        ps   = self.setBlankIfDefault(self.ps,  0)
        seid = self.setBlankIfDefault(self.seid,0)
        fields = ['GRDSET',None,cid,None,None,None,cd,ps,seid]

    def crossReference(self):
        cid  = mesh.Coord(self.cid)
        cd   = mesh.Coord(self.cd)
        #seid = mesh.Super(self.seid)

class GRID(Node):
    type = 'GRID'
    def __init__(self,card):
        Node.__init__(self,card)


        ## Node ID
        self.nid = int(card.field(1))

        ## Grid point coordinate system
        self.cp = card.field(2,0)

        xyz = card.fields(3,6,[0.,0.,0.])  ## @todo is standard nastran to set <0,0,0>as the defaults???
        #displayCard(card)
        #print "xyz = ",xyz
        self.xyz = array(xyz)

        ## Analysis coordinate system
        self.cd = card.field(6,0)

        ## SPC constraint
        self.ps = card.field(7,0)

        ## Superelement ID
        self.seid = card.field(8,0)

        #print "xyz = ",self.xyz
        #print "cd = ",self.cd
        #print "ps = ",self.ps

    def Position(self,debug=False):
        #print type(self.cp)
        return self.cp.transformToGlobal(self.xyz,debug=debug)

    def PositionWRT(self,mesh,cid,debug=False):
        #print type(self.cp)
        coord = mesh.Coord(cid)
        return coord.transformToGlobal(self.xyz,debug=debug)

    def crossReference(self,mesh,grdset=None):
        #print str(self)
        if grdset: # update using a gridset object
            if not self.cp:   self.cp   = grdset.cp
            if not self.cd:   self.cd   = grdset.cd
            if not self.ps:   self.ps   = grdset.ps
            if not self.seid: self.seid = grdset.seid
        self.cp = mesh.Coord(self.cp)
        self.cd = mesh.Coord(self.cd)
        #self.xyzGlobal = coord.transformToGlobal(self.xyz)
        #return self.

    def __repr__(self):
        cp   = self.setBlankIfDefault(self.cp.cid, 0)
        cd   = self.setBlankIfDefault(self.cd.cid, 0)
        ps   = self.setBlankIfDefault(self.ps,  0)
        seid = self.setBlankIfDefault(self.seid,0)
        fields = ['GRID',self.nid,cp]+list(self.xyz)+[cd,ps,seid]
        #print "fields = ",fields
        return self.printCard(fields)

#class RINGAX
