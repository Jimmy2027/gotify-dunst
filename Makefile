install:
	# openrc file
	install gotify-dunst.openrc /etc/init.d/gotify-dunst
	ln -s /etc/init.d/gotify-dunst /etc/init.d/gotify-dunst.$(SUDO_USER) -f
	rc-update add gotify-dunst.$(SUDO_USER) default
	rc-service gotify-dunst.$(SUDO_USER) start

	# files in /usr/lib
	install -d /home/$(SUDO_USER)/.config/gotify-dunst/
	install gotify-dunst.py /home/$(SUDO_USER)/.local/bin/
	install gotify-dunst.conf /home/$(SUDO_USER)/.config/gotify-dunst/

	# create logdir
	install -d /var/log/gotify-dunst
	chown $(SUDO_USER):$(SUDO_USER) /var/log/gotify-dunst

	# files in /usr/share
	install -d $(DESTDIR)$(PREFIX)/share/applications
	install gotify-dunst.desktop $(DESTDIR)$(PREFIX)/share/applications
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps/
	install gotify-16.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps/gotify.png
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/32x32/apps/
	install gotify-32.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/32x32/apps/gotify.png
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/96x96/apps/
	install gotify-96.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/96x96/apps/gotify.png
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps/
	install gotify-128.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps/gotify.png
