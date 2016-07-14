from ROOT import RooAbsPdf

class PDFBuilder(object) :
    __slots__ = ('pars', 'defaultpars', 'pdf', '_pdf', 'results')

    defaultpars = {}
    
    def __init__(self, pars = None, results = None) :
        self.pars = dict(self.defaultpars)
        if pars :
            self.pars.update(pars)
        self.results = results
        
    @property
    def pdf(self) :
        return self._get_pdf()

    def _init_pdf(self) :
        '''So that the PDF is only built when requested, and only once.'''
        self._pdf = self._build_pdf()
        if self.results :
            self._pdf.update_pars(self.results)
        self._get_pdf = self._return_pdf
        return self._pdf

    def _return_pdf(self) :
        return self._pdf
    
    _get_pdf = _init_pdf
        
