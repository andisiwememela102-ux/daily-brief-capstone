PYTHON ?= python
SOURCEDIR = .
BUILDDIR = _build

.PHONY: html clean
html:
	$(PYTHON) -m sphinx -b html $(SOURCEDIR) $(BUILDDIR)/html

clean:
	$(PYTHON) -m sphinx -M clean $(SOURCEDIR) $(BUILDDIR)
