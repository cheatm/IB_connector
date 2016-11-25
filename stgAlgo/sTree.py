
class Params():
    params={}
    plist=[]

    def __init__(self,**params):

        self.params=params
        for key in params.keys():
            self.plist.append(
                (key,len(params[key]),params[key])
            )
        self.len=self.getlen()

    def getlen(self):
        l=0
        for v in self.params.values():
            if l:
               l*=len(v)
            else:
                l+=len(v)
        return l

    def __len__(self):
        return self.len

    def __getitem__(self, item):
        if item<self.len:
            out={}
            l=self.len
            for key,length,param in self.plist:
                l=l/length
                pos=int(item/(l))
                out[key]=param[pos]
                item-=l*pos
            return out

        else:
            raise StopIteration



class STree():

    leaves={}

    def __init__(self,name,type='0',*strategies,**typeStrategies):
        '''

        :param name: name of the tree
        :param strategies: list of strategies names:['entry1','entry2',...]
        :return:
        '''

        self.name=name
        self.type=type
        self.create(type,*strategies,**typeStrategies)

    def createParamBranch(self,params,funcParams,**need):
        inneedParam=need.copy()
        pa=params.copy()
        if self.name in funcParams.keys():
            for p in funcParams[self.name]:
                if p in params:
                    inneedParam[p]=params[p]
                    pa.pop(p)

        for name in self.leaves.keys():
            tree=self.leaves[name]
            if isinstance(tree,STree):
                tree.createParamBranch(pa,funcParams,**inneedParam)

        if len(self.leaves)==0:
            self.__init__(self.name,self.type,**inneedParam)


    def create(self,type,*strategies,**ts):
        leaves={}
        nextType= str(int(type)+1) if type.isdigit() else type

        if len(strategies)>1:
            for s in strategies[0]:
                leaves[s] = STree(s,nextType,*strategies[1:],**ts)

        elif len(strategies)==1:
            for s in strategies[0]:
                leaves[s]= STree(s,nextType,**ts)

        else:
            if len(ts)>0:
                t,leave=ts.popitem()
                for s in leave:
                    leaves[s]=STree(s,t,**ts)


        self.leaves=leaves.copy()

    def showBranchesDict(self,tree,**parentDict):
        thisDict=parentDict.copy()
        thisDict[tree.type]=tree.name
        thisList=[]

        for name in tree.leaves.keys():
            if isinstance(tree.leaves[name],STree):

                next=tree.showBranchesDict(tree.leaves[name],**thisDict)
                thisList.extend(next)
            else :
                thisList.append(thisDict)

        if len(tree.leaves)==0:
            thisList.append(thisDict)

        return thisList

    def showBranches(self,tree,*nameList):
        thisList=[]
        for name in tree.leaves.keys():
            if isinstance(tree.leaves[name],STree):
                leaveList=list(nameList)
                leaveList.append(name)

                thisList.extend(tree.showBranches(tree.leaves[name],*leaveList))
            else :
                thisList.append(nameList)
        if len(tree.leaves)<1:
            thisList.append(nameList)

        return thisList

    def showAllCombination(self):
        combList=[]
        for name in self.leaves.keys():
            tree=self.leaves[name]
            combList.extend(self.showBranchesDict(tree))
        return combList




if __name__ == '__main__':
    pass

