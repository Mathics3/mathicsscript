# A GNU Makefile to run various tasks - compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= admin-tools/git2cl
PYTHON ?= python3
PIP ?= pip3
RM  ?= rm

.PHONY: all build check clean develop dist doc pytest sdist test rmChangeLog

#: Default target - same as "develop"
all: develop

#: build everything needed to install
build:
	$(PYTHON) ./setup.py build

#: Set up to run from the source tree
develop:
	$(PIP) install -e .

#: Install mathicsscript
install:
	$(PYTHON) setup.py install

#: Run tests. You can set environment variable "o" for pytest options
check:
	py.test test $o

# Check StructuredText long description formatting
check-rst:
	$(PYTHON) setup.py --long-description | ./rst2html.py > mathicsscript.html

#: Remove derived files
clean:
	@find . -name "*.pyc" -type f -delete

#: Remove ChangeLog
rmChangeLog:
	$(RM) ChangeLog || true

#: Create source tarball
sdist: check-rst
	$(PYTHON) ./setup.py sdist

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@
