import sys, imp

class CustomImporter(object) :
    __slots__ = ('modulename', 'path')

    def __init__(self, modulename) :
        self.modulename = modulename
        self.path = None
        sys.meta_path.append(self)
        
    def find_module(self, fullname, path = None) :
        if fullname == self.modulename :
            self.path = path
            return self
        return None

    def load_module(self, fullname) :
        if fullname in sys.modules:
            return sys.modules[fullname]
        module_info = imp.find_module(fullname, self.path)
        module = imp.load_module(fullname, *module_info)
        sys.modules[fullname] = module

        self.hack_module(module)
        return module
    
    def hack_module(self, module) :
        pass

def duck_punch(classtype, **functions) :
    '''Add/modify member attributes/functions to/of an existing class.

    .......................... ..... . ......... ........... .................. ..+ 
    .                                        .....       ..                       + 
    .                                      ... +.:....~..:.   ..                  + 
    .                                .. ..~?NMO.?N7~D, .+..                      .+ 
    .                                .M.$MDMDNDZM$.+??.ONMOZ8...:.                + 
    .                              .+.MNNNM.....DMMM$ONMMMN7IN7. .               .? 
    .                        ......DDM,...... ...  MON,.,,.::MN7 .               .I 
    ,                       .....,,8....  ..  .   ..ZM?ZOMN~~MDNM..              .7 
    .                       ,.,NN$.....         ..I..,NNN7NNMN7M,.I+             .$ 
    .                      ..:DN..      .:.     ......,.,OMMNN:N. ..             .I 
    .                    .,. M...      .M., .       . :=..,8. ,8D,O..             Z 
    .                    ....N,.     ....          ..OI...+8NN+M.IM,....          Z 
    .                    .+O8,..    ....            . . .....=N,N.N:$....        .Z 
    .                    . NN.  ... M,   ..,....            . 8NONM,N..          .D 
    .                   ...:D?   .:DM.   .D.O...          ZM .+N:NDD.D.          .8 
    .                    .7D8I.... .    ....,             ..8.,.M8:$7.~ .        .8 
    .              .   . .. ..,:~=.       ............    .+..= ..NON..           D 
    .                  ..8.8D..N87  .   ..M..=$+IMNMN,.... .M$M . NM8$I          .8 
    .                ...+  .?.++N:~7... .M....... ... ...~MM.,?N..NN:O..          D 
    .                  . .7   :.NMN7MN:7M$?.I..,..$..  .....= ,..7I?,7+          .8 
    .                ..,M...   . +...M.. . . NM.., .       ..,.~D$NM~,.          .8 
    .          ..... ?I..    ..N.,O. .   ..  ..   .. ..     ..+D... ...:==??I?IMN7D 
    .    ... ...,.....~7:... ..N$.. .7. .,:....Z$ .. M. . ..  ... ....           ,O 
    .      +.. ..... .. .. .O.DD ..D.: :....$=.N. .$8 . .D..                     .Z 
    .       ...  ,.... .. ...NN. +I. N.. . .  .M ..M 8..D....                    .$ 
    .                       ND,  .O..   .IIN...D. .M..7 .?+ .....                ,$ 
    .    ...             . 7~D.=.....N.  .. ., I..~~,....$=,:.?,~O,.            ..7 
    .                   ..N=M.Z..   ...?.. .....8O...M.IN ...N,MO,,..            .? 
    .                   .Z,D,Z..   ..==,..8I.. =II..D  .  . ..M?M~MM..        .. .I 
    .                  .Z.,.7.      .  ,:..  .:~.:.,..  ..     =.MIN8$.I..... ~+=N= 
    .                ..MM,:= .         .,O.:,.8.7M.MD.        ..DMZ=..8MD.N?O$ZZ~M= 
    .               .,:..:..             . :Z,...   ~.      .   ,~M.~. ..~DNDMM?NM~ 
    .            ...O=..8.                        ..M ...   .   .,,~DO.  .... NDNN~ 
    .            ...?,D  .                        . M ..    ..   .MZ$ .      .   .= 
    . ..          . ....                           ,N?.  ,+.      .NI$.           ~ 
    . .                                            . N..     ..   .7MO..         .: 
    .      ..      ..  .          .                .II..    ...   .?=D.  .    ....: 
    DMMNDDNNDDDNDDNNNDDDDNDNNDDDNDDDDDD888D888OD888D8OD8D8D8888OOOO$MNOOZ$???$I$$$, 
                                                                     GlassGiant.com
'''
    
    for funcName, func in functions.iteritems() :
        if hasattr(classtype, funcName) :
            setattr(classtype, '__orig_' + funcName,
                    getattr(classtype, funcName))
        setattr(classtype, funcName, func)


class ModuleDuckPuncher(CustomImporter) :
    __slots__ = ('attrs',)

    def __init__(self, modulename, **attrs) :
        CustomImporter.__init__(self, modulename)
        self.attrs = attrs

    def hack_module(self, module) :
        duck_punch(module, **self.attrs)

def hacked_ROOT_getattr(self, attr) :
    obj = self.__orig___getattr__(attr)
    if attr in self._classhacks :
        duck_punch(obj, **self._classhacks[attr])
        del self._classhacks[attr]
    self.__class__.__orig___getattr2 = self.__getattr__
    self.__class__.__getattr__ = hacked_ROOT_getattr2
    return obj

def hacked_ROOT_getattr2(self, attr) :
    obj = self.__orig___getattr2(attr)
    if attr in self._classhacks :
        duck_punch(obj, **self._classhacks[attr])
        del self._classhacks[attr]
        if not self._classhacks :
            self.__class__.__getattr__ = self.__class__.__orig___getattr2
            del self.__class__.__orig___getattr2
            del self.__class__._classhacks
    return obj

class ROOTDuckPuncher(ModuleDuckPuncher) :

    def __init__(self, **classhacks) :
        ModuleDuckPuncher.__init__(self, 'ROOT',
                                   __getattr__ = hacked_ROOT_getattr,
                                   _classhacks = classhacks)
        
    def hack_module(self, module) :
        ModuleDuckPuncher.hack_module(self, module.__class__)
        
def duck_punch_RooRealVar() :
    '''Hijack the RooRealVar class and add some useful functionality.'''

    def new(name, title, value = None, xmin = -sys.float_info.max,
            xmax = sys.float_info.max, error = None, errLow = None,
            errHigh = None, unit = None, constant = None) :
        '''Constructor that also allows setting errors.'''
        v = ROOT.RooRealVar(name, title, xmin, xmax)
        kwargs = dict(locals())
        for arg in 'name', 'title', 'xmin', 'xmax', 'v' :
            del kwargs[arg]
        v.set_attrs(**kwargs)
        return v
    
    new = staticmethod(new)
        
    def set_attrs(self, name = None, title = None,
                  value = None, xmin = None,
                  xmax = None, error = None, errLow = None,
                  errHigh = None, unit = None, constant = None) :
        '''Set the value, range, error, asymmetric errors, unit, and constant
        attributes.'''

        if None != name :
            self.SetName(name)
        if None != title :
            self.SetTitle(title)
        if None != xmin and None != xmax :
            self.setRange(xmin, xmax)
        if (None != xmin and None == xmax) \
           or (None == xmin and None != xmax) :
            raise ValueError('Both xmax and xmin must be set to assign the '\
                             'range! Got xmin = {0!r} and xmax = {1!r}'.format(xmin, xmax))
        if None != value :
            self.setVal(value)
        if None != error :
            self.setError(error)
        if None != errLow and None != errHigh :
            self.setAsymError(errLow, errHigh)
        if (None != errLow and None == errHigh) \
           or (None == errLow and None != errHigh) :
            raise ValueError('Both errLow and errHigh must be set to'\
                             ' assign asymmetric errors!'\
                             'Got errLow = {0!r} and errHigh = {1!r}'.format(errLow, errHigh))
        if None != unit :
            self.setUnit(unit)
        if None != constant :
            self.setConstant(constant)

    def get_attrs(self) :
        return dict(name = self.GetName(), title = self.GetTitle(),
                    value = self.getVal(), 
                    xmin = self.getMin(), xmax = self.getMax(),
                    error = self.getError(), errLow = self.getErrorLo(),
                    errHigh = self.getErrorHi(), unit = self.getUnit(),
                    constant = self.isConstant())
                    
    def to_string(self, registry = None, addToRegistry = True) :
        selfStr = 'RooFitter.RooUtils.RooNew(ROOT.RooRealVar, '
        selfStr += 'name = {name!r}, title = {title!r}, '
        selfStr += 'value = {value!r}, '
        selfStr += 'xmin = {xmin!r}, xmax = {xmax!r}, '
        selfStr += 'error = {error!r}, errLow = {errLow!r}, errHigh = {errHigh!r}, '
        selfStr += 'unit = {unit!r}, constant = {constant!r}, '
        selfStr += 'registry = {registry!s}, addToRegistry = {addToRegistry!r})'
        return selfStr.format(registry = registry, addToRegistry = addToRegistry,
                              **self.get_attrs())

    def copy_attrs(self, other) :
        self.set_attrs(**other.get_attrs())
    
    def __repr__(self) :
        return self.to_string(addToRegistry = False)
    
    return locals()

def duck_punch_RooAbsPdf() :

    dataset = None

    def get_data(self, *args) :
        data = filter(lambda arg : isinstance(arg, ROOT.RooAbsData), args + (self.dataset,))
        if not data :
            return None, None
        data = data[0]
        args = filter(lambda arg : not isinstance(arg, ROOT.RooAbsData), args)
        return data, args
    
    def fit(self, *args) :
        data, args = self.get_data(*args)
        if not data :
            return None
        return self.fitTo(data, ROOT.RooFit.Save(True), *args)

    def plot_fit(self, data = None, pullCanvHeight = 0.2, canvArgs = (),
                 dataPlotArgs = ()) :
        '''Plot the fit over the data for the given plotVar with the pull below. If 
        pullCanvHeight == 0. the pull isn't drawn. If extended == True the fit PDF 
        is normalised according to the fitted yields of the extended PDF, else it's
        normalised to the data. canvArgs are passed to the TCanvas constructor.'''

        if None == data :
            if None == self.dataset :
                return None
            data = self.dataset

        plotVars = self.getObservables(data)
        if len(plotVars) > 1 :
            print 'Sorry, only 1D plotting is implemented so far!'
            return
    
        plotVar = plotVars.first()
    
        try :
            canv = ROOT.TCanvas(*canvArgs)
        except :
            print 'Failed to construct TCanvas with args', repr(canvArgs)
            raise

        canv.cd()
        mainPad = ROOT.TPad('mainPad', 'mainPad', 0., pullCanvHeight, 1., 1.)
        mainPad.Draw()

        mainFrame = plotVar.frame()
        data.plotOn(mainFrame, *dataPlotArgs)
        if hasattr(self, 'extendMode') and self.extendMode() != 0 :
            # Change from RooAbsReal.RelativeExtended, as given in the manual, as it doesn't
            # exist.
            self.plotOn(mainFrame, ROOT.RooFit.Normalization(1.0, ROOT.RooAbsReal.RelativeExpected))
        else :
            self.plotOn(mainFrame)
        mainPad.cd()
        mainFrame.Draw()
    
        if pullCanvHeight <= 0. :
            return locals()
    
        canv.cd()
        pullPad = ROOT.TPad('mainPad', 'mainPad', 0., 0., 1., pullCanvHeight)
        pullPad.Draw()

        # from /opt/local/share/root5/doc/root/tutorials/roofit/rf109_chi2residpull.C
        pullFrame = plotVar.frame()
        pullHist = mainFrame.pullHist()
        pullFrame.addPlotable(pullHist, 'P')
        pullPad.cd()
        pullFrame.Draw()

        return locals()

    def update_pars(self, resultSet) :
        ownpars = dict((par.GetName(), par) for par in self.getVariables())
        for par in resultSet.constPars().to_list() + resultSet.floatParsFinal().to_list() :
            if par.GetName() in ownpars :
                ownpars[par.GetName()].copy_attrs(par)
    
    return locals()

def duck_punch_RooArgSet() :

    def __iter__(self) :
        return iter(self.to_list())
    
    def to_list(self) :
        i = self.fwdIterator()
        return [i.next() for j in xrange(len(self))]

    def intersection(self, other) :
        return list(set(self).intersection(set(other)))

    def union(self, other) :
        return list(set(self).union(set(other)))
                    
    return locals()

def duck_punch_RooArgList() :

    def __iter__(self) :
        return iter(self.to_list())
    
    def to_list(self) :
        i = self.fwdIterator()
        return [i.next() for j in xrange(len(self))]
    
    return locals()

def duck_punch_RooAddPdf() :

    def new(name, title, component1, component2, *components, **kwargs) :
        '''Make a RooAddPdf with the given components, which should be 
        (RooRealVar, RooAbsPdf) pairs.'''
    
        components = (component1, component2) + components
        try :
            if isinstance(components[-1], (tuple, list)) :
                return ROOT.RooAddPdf(name, title, ROOT.RooArgList(*[pdf for n, pdf in components]),
                                      ROOT.RooArgList(*[n for n, pdf in components]))
            else :
                if len(components) > 2 :
                    if not 'registry' in kwargs :
                        raise KeyError("'registry' keyword is required so sub-PDFs can be registered!")
                    component2 = \
                        RooFitter.RooUtils.RooNew(ROOT.RooAddPdf, 'sub_' + name, 'Sub. ' + title,
                                                  *components[1:], registry = kwargs['registry'])
                return ROOT.RooAddPdf(name, title, ROOT.RooArgList(component1[1], component2),
                                      ROOT.RooArgList(component1[0]))

        except (ValueError, TypeError) as excpt :
            excpt.message += '''
Components must be pairs of (RooRealVar, RooAbsPdf), except the last 
which can be a RooAbsPdf without a coefficient.
Got ''' + repr(components)
            raise excpt.__class__(excpt.message)

    new = staticmethod(new)

    return locals()

def duck_punch_RooDataSet() :

    def to_tree(self) :
        treedata = ROOT.RooTreeDataStore(self.GetName(), self.GetTitle(), self.get(0),
                                         self.store())
        return treedata.tree(), treedata

    return locals()
    
ROOTDuckPuncher(RooRealVar = duck_punch_RooRealVar(),
                RooAbsPdf = duck_punch_RooAbsPdf(),
                RooArgSet = duck_punch_RooArgSet(),
                RooArgList = duck_punch_RooArgList(),
                RooAddPdf = duck_punch_RooAddPdf(),
                RooDataSet = duck_punch_RooDataSet())
import ROOT
import RooFitter
