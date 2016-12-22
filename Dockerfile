FROM scratch
MAINTAINER \
[Ergün Salman <admin@limelinux.com>] \

ADD chroot.tar.xz /

RUN pisi rr depo && service dbus start



CMD ["/usr/bin/bash"]
