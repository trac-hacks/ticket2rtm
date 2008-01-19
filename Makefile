PLUGINS_DIR=~/sandbox/trac-sandbox/plugins/
all:
	python setup.py develop -md $(PLUGINS_DIR)
