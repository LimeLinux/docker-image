FROM scratch

ADD lime_2016-12-25.tar.xz /

RUN chmod o+x /usr/lib/dbus-1.0/dbus-daemon-launch-helper

RUN dbus-uuidgen --ensure
RUN dbus-daemon --system

