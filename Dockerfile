FROM scratch
MAINTAINER \
[Ergün Salman <admin@limelinux.com>] \

ADD lime_2016-12-25.tar.xz /

RUN chmod o+x /usr/lib/dbus-1.0/dbus-daemon-launch-helper
RUN rc-status && service dbus start



CMD ["/usr/bin/bash"]
