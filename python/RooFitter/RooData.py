import os, sys, ROOT
from ROOT import RooDataSet, TFile, RooArgSet, RooFit, RooCmdArg, TObject, RooRealVar, \
    TNamed

def RooDataCacheFactory(attr1, *attrs) :
    # So you can pass a list or tuple of attributes, or strings.
    if not isinstance(attr1, str) :
        attrs = tuple(attr1) + attrs
    else :
        attrs = (attr1,) + attrs

    class RooDataCache(object) :
        '''Cache just about anything in a .root file. Non-ROOT objects are
        repr'd and stored in the title of a TNamed.'''

        __slots__ = ('name', 'savefname', 'initstring', 'fileresident', 'datafile', '_data', '_get_data') + attrs
        objnames = attrs

        def __init__(self, name, savefname, initstring, fileresident = False) :
            '''name is the prefix given to the objects saved in the .root file.
            savefname is the name of the file to save the objects in. 
            initstring is the initialisation string should declare a variable of 
            the same name as the attribute. Eg:
            
            histocache = RooDataCache('histocache', 'histos.root', 'histo', 'histo = ROOT.TH1F()')
            histo = histocache.histo
            
            The initialisation string is also stored in the .root file. If it changes
            then the objects are reinitialised, otherwise they're just loaded from
            the file.
            
            Non-ROOT objects can be stored too - they're repr'd and stored in the 
            title of a TNamed. When loading from the file the title of a TNamed
            is eval'd. Eg:
            
            bincache = RooDataCache('bincache', 'bins.root', 'bins', 'bins = [1,2,3,4]')
            bins = bincache.bins
            
            The initialisation string can be anything that can be passed to exec.'''

            self.name = name
            self.savefname = savefname
            self.initstring = initstring
            self.fileresident = fileresident
            self.datafile = None
            self._data = None
            self._get_data = self._retrieve_data
            
        @property
        def data(self) :
            return self._get_data()

        def _return_data(self) :
            return self._data

        def _init_data(self) :
            localns = dict(locals())
            if self.fileresident :
                self.datafile = self.get_save_file('update')
            exec self.initstring in globals(), localns
            data = dict((name, localns[name]) for name in self.objnames)
            return data

        def _init_string_name(self) :
            return self.name + '_initstring'

        def _save_names(self) :
            return dict((name, self.name + '_' + name) for name in self.objnames)
        
        def _from_file(self) :
            savefile = self.get_save_file()
            if not savefile :
                return None
            if self.fileresident :
                self.datafile = savefile
            initdata = savefile.Get(self._init_string_name())
            if not initdata :
                savefile.Close()
                return None
            if initdata.GetTitle() != self.initstring :
                savefile.Close()
                return None
            data = dict((name, savefile.Get(savename)) for name, savename in \
                        self._save_names().iteritems())
            if not all(data.values()) :
                savefile.Close()
                return None
            for name, val in data.iteritems() :
                if val.__class__ == ROOT.TNamed :
                    try :
                        data[name] = eval(val.GetTitle())
                    except :
                        pass
                # Make sure that objects normally owned by a TFile are disowned.
                if not self.fileresident and savefile.GetList().FindObject(val) \
                   and hasattr(val, 'SetDirectory') :
                    val.SetDirectory(None)
            if not self.fileresident :
                savefile.Close()
            return data

        def update(self) :
            data = self._init_data()
            self._data = data
            self.save(True)
            return data
        
        def _retrieve_data(self) :
            self._get_data = self._return_data
            data = self._from_file()
            if not data :
                self.update()
            else :
                self._data = data
            return self._data

        def get_save_file(self, mode = 'read') :
            # Have to use TFile.Open to check if file exists for mass storage files.
            savefile = TFile.Open(self.savefname, mode)
            if None == savefile or savefile.IsZombie() :
                return None
            return savefile

        def save(self, force = False) :
            # ensure the data's been retrieved.
            self.data
            # only save if necessary.
            if not force and self._from_file() :
                return
            if self.fileresident :
                savefile = self.datafile
            else :
                savefile = self.get_save_file('update')
            for name, savename in self._save_names().iteritems() :
                obj = self.data[name]
                if not isinstance(obj, ROOT.TObject) :
                    obj = ROOT.TNamed(savename, repr(obj))
                obj.Write(savename, TObject.kWriteDelete + TObject.kSingleKey)
            TNamed(self._init_string_name(), self.initstring).Write(self._init_string_name(), TObject.kOverwrite)
            if not self.fileresident :
                savefile.Close()

        def __del__(self) :
            if self.fileresident and self.datafile :
                self.datafile.Close()
                
    for attr in attrs :
        setattr(RooDataCache, attr, property(fget = eval('lambda self : self.data[{attr!r}]'.format(attr = attr))))

    return RooDataCache

def RooScriptCacheFactory(attr1, *attrs) :

    class RooScriptCache(RooDataCacheFactory(attr1, *attrs)) :

        __slots__ = ('scriptname','args')
        
        def __init__(self, name, savefname, scriptname, args = [], fileresident = False) :
            self.scriptname = os.path.expandvars(scriptname)
            self.args = [self.scriptname] + args
            super(self.__class__, self).__init__(name, savefname, '', fileresident = fileresident)

        def _retrieve_data(self) :
            # So the script is only read when the data is requested.
            # This only triggers an update if the script itself has changed, and not
            # any of its dependencies. 
            # Could be more sensible to import the script rather than reading it and
            # exec'ing it. Could potentially check its last modification time and
            # compare to the last update of the cache, maybe also checking dependencies
            # and their last update, though that could get quite read intensive.
            # Options there are modulefinder builtin module:
            # import modulefinder
            # m = modulefinder.ModuleFinder()
            # m.load_file(f)
            # m.modules
            # Or else there's snakefood which is non-SL but has the ability to filter
            # out builtin modules.
            # Can use os.path.getmtime to get the modification time of a file. 
            with open(self.scriptname) as f :
                self.initstring = f.read()
            # Bit of a nasty hack, not sure how else to do it though. 
            sys.argv = self.args
            return super(self.__class__, self)._retrieve_data()

    return RooScriptCache

def RooDataCache(name, savefname, objnames, initstring, fileresident = False) :
    return RooDataCacheFactory(objnames)(name, savefname, initstring, fileresident = fileresident)

def RooScriptCache(name, savefname, objnames, scriptname, args = [], fileresident = False) :
    return RooScriptCacheFactory(objnames)(name, savefname, scriptname, args = args, fileresident = fileresident)


class RooTreeData(RooDataCacheFactory('dataset')) :

    __slots__ = ('name', 'title', 'inputfname', 'treename', 'selection', 'datavars',
                 'savefname')

    def __init__(self, savefname, name, title, fname, treename, datavars,
                 selection = None) :
        self.title = title
        self.datavars = datavars
        self.inputfname = fname
        self.treename = treename
        self.selection = selection
        
        datavarnames = [var.GetName() for var in datavars]
        initstring = '''
datavarnames = {datavarnames!r}
selection = {selection!r}
f = TFile.Open(self.inputfname)
tree = f.Get(self.treename)
dataset = RooDataSet(self.name + '_dataset', self.title,
                     RooArgSet(*self.datavars), RooFit.Import(tree),
                     (RooFit.Cut(self.selection) if self.selection else RooCmdArg()))
'''.format(datavarnames = datavarnames, selection = self.selection)

        super(self.__class__, self).__init__(name, savefname, initstring)
        
    #  __slots__ = ('name', 'title', 'inputfname', 'treename', 'selection', 'datavars',
    #              'savefname', '_dataset')

    # @property
    # def dataset(self) :
    #     if None == self._dataset :
    #         self._dataset = self._retrieve_dataset()
    #         self.datavars = self._dataset.get(0).to_list()
    #         self.save()
    #     return self._dataset

    # @dataset.setter
    # def dataset(self, value) :
    #     if not isinstance(value, (type(None), RooDataSet)) :
    #         raise TypeError('dataset must be a RooDataSet or None!')
    #     self._dataset = value
        
    # def __init__(self, savefname, name, title, fname, treename, datavars,
    #              selection = None, dataset = None) :
    #     self.name = name
    #     self.title = title
    #     self.inputfname = os.path.expandvars(fname)
    #     self.treename = treename
    #     self.selection = selection
    #     self.datavars = datavars
    #     self.savefname = os.path.expandvars(savefname)
    #     self.dataset = dataset

    # def _new_dataset(self) :
    #     f = TFile.Open(self.inputfname)
    #     tree = f.Get(self.treename)

    #     # I thought this might be more memory efficient than the other option:
    #     # RooDataSet(name, title, tree, RooArgSet(var1, *moreVars))
    #     # but it still somehow uses an absurd amount of memory (several times
    #     # the size of the file) when reading in the data, and then releases
    #     # most of it. 
    #     # Using ImportFromFile crashes, no idea why. 

    #     return RooDataSet(self.name, self.title,
    #                       RooArgSet(*self.datavars), RooFit.Import(tree),
    #                       (RooFit.Cut(self.selection) if self.selection else RooCmdArg()))

    # def has_own_vars(self, dataset) :
    #     '''Check that the variables in the dataset is a superset of
    #     the variables expected.'''
    #     dsvarnames = set(v.GetName() for v in dataset.get(0).to_list())
    #     ownvarnames = set(v.GetName() if isinstance(v, RooRealVar) else v for v in self.datavars)
    #     return dsvarnames.issuperset(ownvarnames)

    # def matches_data(self, dataset) :
    #     return (None != dataset
    #             and dataset.numEntries() != 0
    #             and self.has_own_vars(dataset)
    #             and (self._dataset == None or self._dataset.numEntries() == dataset.numEntries()))

    # def matches(self, savefile) :
    #     dataset = savefile.Get(self.name)
    #     selection = savefile.Get(self.name + '_selection')
    #     return (None != selection and None != dataset
    #             and selection.GetTitle() == self.selection and self.matches_data(dataset))
            
    # def _retrieve_dataset(self, forceupdate = False) :
    #     if forceupdate :
    #         return self._new_dataset()
    #     savefile = self.get_save_file()
    #     if None == savefile :
    #         return self._new_dataset()
    #     if not self.matches(savefile) :
    #         savefile.Close()
    #         return self._new_dataset()
    #     # This seems to be OK, the RooDataSet isn't deleted when the
    #     # file is closed.
    #     dataset = savefile.Get(self.name)
    #     savefile.Close()
    #     return dataset
        
    # def save(self, force = False) :
    #     # Make sure the dataset has been retrieved.
    #     self.dataset
    #     # First check if the file exists.
    #     savefile = self.get_save_file()
    #     # If not, create it.
    #     if None == savefile :
    #         savefile = self.get_save_file('recreate')
    #     else :
    #         # If the dataset is already in the file matches and
    #         # matches this one,and force = False, then no need to save.
    #         filedataset = savefile.Get(self.name)
    #         if not force and self.matches(savefile) :
    #             savefile.Close()
    #             return None
    #         # Else open the file in update mode.
    #         savefile.ReOpen('update')
    #     TNamed(self.name + '_selection', self.selection).Write(self.name + '_selection', TObject.kOverwrite)
    #     self._dataset.Write(self.name, TObject.kOverwrite)
    #     savefile.Close()
    #     return True
        
