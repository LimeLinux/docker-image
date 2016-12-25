FROM scratch

ADD lime_2016-12-25.tar.xz /

RUN chmod o+x /usr/lib/dbus-1.0/dbus-daemon-launch-helper

RUN rc-status && rc-service dbus restart && pisi it http://ciftlik.pisilinux.org/2.0-stable/g/gawk/gawk-4.1.3-2-p2-x86_64.pisi --ignore-check --ignore-dep --ignore-safety -dv
