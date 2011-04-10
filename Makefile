all: help

help:
	@echo "setup-dev      add this project to your local python library"

test:
	python src/puppeteer/ui/tkinter.py

setup-dev:
	mkdir -p ~/.local/lib/python2.6/site-packages
	ln -fs `pwd`/src/puppeteer ~/.local/lib/python2.6/site-packages
