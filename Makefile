
all: nethost

nethost: *.py
	zip nethost.zip *.py
	cat shebang nethost.zip > nethost
	chmod +x nethost

install: nethost
	cp nethost $${HOME}/bin/

.PHONY: install
