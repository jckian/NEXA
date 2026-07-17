#   Ellipse（橢圓）

import math
import numpy as np
import random



class Agent:
    def __init__(self, x,y,z,area,r1,r2,programType,programCategory,boundary):
        self.x = x
        self.y = y
        self.z = z
        self.pos = (x,y)
        self.area = area
        self.radx = r1/2
        self.rady = r2/2
        self.programType = programType
        self.programCategory = programCategory
        self.boundary = boundary
        self.death = True

        #   vvvvvvvvvvvvvvv    SET RULES HERE
        self.adjacents = []
        # Use substring matching so 'fire stair and elevator 1/2' are also detected as cores
        if ('fire stair and freight elevator' in programType or
                'fire stair and elevator' in programType):
            bound, boundDis, inside = self.boundary_vector()
            self.pos = self.add(self.pos, bound)
            self.death = False
        #   GPT may output different name (staff toilet / public toilet), don't use "==", use "in"
        if 'toilets' in programType:
            self.adjacents.append('fire stair and elevator')
        elif 'storage' in programType:
            self.adjacents.append('fire stair and freight elevator')
        elif 'loading' in programType:
            self.adjacents.append('fire stair and freight elevator')
        elif 'mechanical' in programType:
            self.adjacents.append('fire stair and elevator')
        elif 'fitting' in programType:
            self.adjacents.append('display')




    def distance_to(self, other):
        x,y = self.pos
        ox,oy = other
        return math.sqrt((x-ox)**2 + (y-oy)**2)

    #   checking all the point's contex 用p0對每個頂點的向量及xy位置
    def inside_boundary(self,px,py):
        n = len(self.boundary)
        inside = False
        x1, y1 = self.boundary[0]
        for i in range(1, n + 1):
            x2, y2 = self.boundary[i % n]
            if py > min(y1, y2):
                if py <= max(y1, y2):
                    if px <= max(x1, x2):
                        if y1 != y2:
                            xinters = (py - y1) * (x2 - x1) / (y2 - y1) + x1
                        if x1 == x2 or px <= xinters:
                            inside = not inside
            x1, y1 = x2, y2
        return inside

    def pointInEllipse(self,px,py,cx,cy,a,b):
        return ((px - cx) / a)**2 + ((py - cy) / b)**2 <= 1

    def ellipsesOverlap(self,p1, rx1,ry1,p2,rx2,ry2):
        cx1, cy1 = p1
        cx2, cy2 = p2


        a1, b1 = rx1, ry1
        a2, b2 = rx2, ry2

        d1x = cx1-cx2
        d1y = cy1-cy2
        cdis = self.mag((d1x, d1y))
        maxRad = max(a1,b1)+max(a2,b2)
        if cdis > maxRad:
            return (0,0),0,False
        t = np.linspace(0,2*np.pi,64)
        maxpen1 = 0
        deepestPt1 = None
        for angle in t:
            px = cx1+a1*np.cos(angle)
            py = cy1+b1*np.sin(angle)
            if self.pointInEllipse(px,py,cx2,cy2,a2,b2):
                dx = px-cx2
                dy = py-cy2
                disC = self.mag((dx, dy))
                if disC > 0:
                    dirx = dx/disC
                    diry = dy/disC
                    a2p = np.arctan2(dy,dx)
                    boundx = cx2+a2*np.cos(a2p)
                    boundy = cy2+b2*np.sin(a2p)
                    pen = self.mag((px-boundx, py-boundy))
                    if pen > maxpen1:
                        maxpen1 = pen
                        deepestPt1 = (px,py,dirx,diry)

        maxpen2 = 0
        deepestPt2 = None
        for angle in t:
            px = cx2+a2*np.cos(angle)
            py = cy2+b2*np.sin(angle)
            if self.pointInEllipse(px,py,cx1,cy1,a1,b1):
                dx = px-cx1
                dy = py-cy1
                disC = self.mag((dx, dy))
                if disC > 0:
                    dirx = dx/disC
                    diry = dy/disC
                    a2p = np.arctan2(dy,dx)
                    boundx = cx1+a1*np.cos(a2p)
                    boundy = cy1+b1*np.sin(a2p)
                    pen = self.mag((px-boundx, py-boundy))
                    if pen > maxpen2:
                        maxpen2 = pen
                        deepestPt2 = (px,py,dirx,diry)
        if maxpen1 == 0 and maxpen2 == 0:
            return (0,0),0,False

        if maxpen1 >= maxpen2 and deepestPt1:
            px,py,dirx,diry = deepestPt1
            sep = maxpen1
            vector = (dirx*sep, diry*sep)
        elif deepestPt2:
            px,py,dirx,diry = deepestPt2
            sep = maxpen2
            vector = (-dirx*sep, -diry*sep)
        else:
            dx = cx2-cx1
            dy = cy2-cy1
            dist = self.mag((dx, dy))
            if dist > 0:
                sep = (a1+a2) - dist
                vector = (dx/dist*sep, dy/dist*sep)
            else:
                vector = (a1+a2,0)
            sep = self.mag(vector)
        mag = self.mag(vector)
        return vector,mag,True



    def point_to_seg_dist(self,p,a,b):
        ab = (b[0] - a[0], b[1] - a[1])
        ap = (p[0] - a[0], p[1] - a[1])

        ab_len_sq = ab[0] ** 2 + ab[1] ** 2

        if ab_len_sq == 0:
            return math.dist(p, a), a
        t = max(0, min(1, (ap[0] * ab[0] + ap[1] * ab[1]) / ab_len_sq))
        closest = (a[0] + t * ab[0], a[1] + t * ab[1])
        return math.dist(p, closest), closest

    def cp_polygon(self,point):
        min_dist = float(99999999.9)
        closest = None
        for i in range(len(self.boundary)):
            a = self.boundary[i]
            i2 = i+1
            if i2 > len(self.boundary)-1:
                i2 = 0
            b = self.boundary[i2]

            dist, pt = self.point_to_seg_dist(point, a, b)

            if dist < min_dist:
                min_dist = dist
                closest = pt

        return min_dist, closest


    def sub(self, v1, v2):
        v1x, v1y = v1
        v2x, v2y = v2
        vec = (v1x - v2x, v1y - v2y)
        return vec
    def add(self,v1,v2):
        v1x, v1y = v1
        v2x, v2y = v2
        vec = (v2x + v1x, v2y + v1y)
        return vec
    def mag(self,v):
        x,y = v
        return math.sqrt(x**2 + y**2)
    def scale(self, v1, fac):
        x,y = v1
        v2 = (x * fac, y * fac)
        return v2
    def normalize(self, inVec):
        x, y = inVec
        mag = math.sqrt(x*x + y*y)
        if mag > 0:
            return (x / mag, y / mag)
        return (0.0, 0.0)

    #   限制移動距離
    def limit(self, inVec, max):
        x, y = inVec
        x1, y1 = 0,0
        if abs(x) > max:
            x1 = max
            if x < 0:
                x1 = x1*-1
        else:
            x1 = x
        if abs(y) > max:
            y1 = max
            if y < 0:
                y1 = y1*-1
        else:
            y1 = y
        outVec = (x1, y1)
        return outVec



    ####behavior functions####
    def boundary_vector(self):
        cx,cy = self.pos
        a = self.radx
        b = self.rady

        t = np.linspace(0,2*np.pi,64)
        ex = cx+a*np.cos(t)
        ey = cy+b*np.sin(t)
        epoints = list(zip(ex,ey))

        out_points = []
        for px,py in epoints:
            if not self.inside_boundary(px,py):
                out_points.append((px,py))
        if len(out_points) == 0:
            return (0,0),0,True

        vectors = []
        for px,py in out_points:
            mindist = 999999999.9
            myVec = None
            for i in range(len(self.boundary)):
                p1 = self.boundary[i]
                i2 = i+1
                if i2 > len(self.boundary)-1:
                    i2 = 0
                p2 = self.boundary[i2]
                dis, cp = self.point_to_seg_dist((px,py),p1,p2)
                vx = cp[0]-px
                vy = cp[1]-py
                if dis < mindist:
                    mindist = dis
                    myVec = (vx,vy)
            if myVec is not None:
                vectors.append(myVec)

        maxdist = 0.00000
        outVec = (0,0)
        for v in vectors:
            dis = self.mag(v)
            if dis > maxdist:
                maxdist = dis
                outVec = v
        tol = .01
        if maxdist >0:

            factor = (maxdist+tol)/maxdist
            outVec = self.scale(outVec, factor)
            maxdist = maxdist+tol
        return outVec, maxdist, False


    def adjVec(self, other):
        cx1,cy1 = self.pos
        cx2,cy2 = other.pos
        a1 = self.radx
        b1 = self.rady
        a2 = other.radx
        b2 = other.rady
        dx = cx2-cx1
        dy = cy2-cy1
        cDist =self.mag((dx,dy))

        if cDist == 0:
            td = a1+a2
            newCx2 = cx1 + td
            newCy2 = cy1
            vec = (td,0)
            return vec, True
        dirx = dx/cDist
        diry = dy/cDist
        ang = np.arctan2(diry,dirx)
        r1 = (a1 * b1) / np.sqrt((b1 * np.cos(ang)) ** 2 + (a1 * np.sin(ang)) ** 2)
        r2 = (a2 * b2) / np.sqrt((b2 * np.cos(ang)) ** 2 + (a2 * np.sin(ang)) ** 2)
        td = r1+r2
        overlapping = cDist < td
        newCx2 = cx1 + dirx*td
        newCy2 = cy1 + diry*td
        vec = (cx2-newCx2,cy2-newCy2)
        outDis = cDist - td
        return vec, overlapping, outDis


    def update(self,aList):
        if self.death:
            popList = aList[self.z]
            acc = (0,0)
            avd = (0,0)
            coh = (0,0)
            adj = (0,0)
            tDir = (0,0)
            #check overlap with other agents
            for i in range(len(popList)):
                if not popList[i] == self:
                    ovec, dis, iover = self.ellipsesOverlap( self.pos, self.radx, self.rady, popList[i].pos, popList[i].radx, popList[i].rady)
                    if iover:
                        avd = self.add(avd,ovec)
                    elif dis > 0:
                        v,test,oDis = self.adjVec(popList[i])
                        if oDis != 0:
                            factor = 1.0 / (oDis**2)
                            temp = self.normalize(v)
                            temp = self.scale(temp, factor)
                            coh = self.add(coh, temp)
                    # adjacency: allow substring matching so types like 'fire stair and elevator 1' match 'fire stair and elevator'
                    for adjType in self.adjacents:
                        try:
                            if adjType in popList[i].programType:
                                v2, test2, oDis2 = self.adjVec(popList[i])
                                adj = self.add(adj, v2)
                                break
                        except Exception:
                            # defensive: if programType is not a string
                            pass

            #   FIX toilets in the same position on every floor
            if self.z > 0 and 'toilets' in self.programType:
                indBelow = self.z-1
                tList = aList[indBelow]
                for i in range(len(tList)):
                    if 'toilets' in tList[i].programType:
                        #move towards the other toilet
                        tDir = self.sub(tList[i].pos,self.pos)






            coh = self.normalize(coh)
            coh = self.scale(coh,.01)
            avd = self.limit(avd,.01)
            #tDir = self.limit(tDir,.1)

            acc = self.add(acc,coh)
            acc = self.add(acc,avd)
            acc = self.add(acc,tDir)

            #acc = self.normalize(acc)
            acc = self.limit(acc,.01)
            self.pos = self.add(self.pos,acc)
            self.pos = self.add(self.pos,adj)
            # check for boundary intersect
            bound,boundDis,inside = self.boundary_vector()

            if not inside:
                #print(boundDis)
                self.pos = self.add(self.pos,bound)



    def outputValues(self):
        outString = str(self.pos[0]) + "," + str(self.pos[1]) + "," + str(self.z) + "," + str(self.area) + "," +str(self.radx) +',' +str(self.rady)+','+ str(self.programType) + "," + str(self.programCategory)
        return outString

    @staticmethod
    def ensure_toilets_per_floor(aList, boundary, area=80, r1=4.0, r2=5.0, programType='toilets', programCategory='public'):
        """Ensure every floor in aList has at least one toilets Agent.

        aList: list of lists where each sublist contains Agent instances for that floor (indexed by z)
        boundary: polygon used for Agent placement (list of (x,y) tuples)
        """
        # simple centroid fallback for placement
        if not boundary:
            cx, cy = 0.0, 0.0
        else:
            xs = [p[0] for p in boundary]
            ys = [p[1] for p in boundary]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)

        for level in range(len(aList)):
            has_toilet = False
            for a in aList[level]:
                try:
                    if 'toilets' in a.programType:
                        has_toilet = True
                        break
                except Exception:
                    continue
            if not has_toilet:
                new_agent = Agent(cx, cy, level, area, r1, r2, programType, programCategory, boundary)
                aList[level].append(new_agent)


