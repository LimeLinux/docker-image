#!/usr/bin/python
# -*- coding: utf-8 -*-
# Modified from https://github.com/Pardus-Linux/pisi/blob/master/scripts/pisi-sandbox
# 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

import os
import shutil
import subprocess
import sys
import stat
import time
import socket
import getopt
import dbus
import datetime

def wait_bus(unix_name, timeout=5, wait=0.1, stream=True):
    import socket
    import time
    if stream:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    while timeout > 0:
        try:
            sock.connect(unix_name)
            return True
        except:
            timeout -= wait
        time.sleep(wait)
    return False

def connectToDBus(path):
    global bus
    bus = None
    for i in range(20):
        try:
            print("trying to start dbus..")
            bus = dbus.bus.BusConnection(address_or_type="unix:path=%s/run/dbus/system_bus_socket" % path)
            break
        except dbus.DBusException:
            time.sleep(1)
            print("wait dbus for 1 second...")
    if bus:
        return True
    return False

def chroot_comar(output_dir):
    if os.fork() == 0:
        # Workaround for creating ISO's on 2007 with PiSi 2.*
        # Create non-existing /var/db directory before running COMAR
        try:
            os.makedirs(os.path.join(output_dir, "var/db"), 0700)
        except OSError:
            pass
        os.chroot(output_dir)
        if not os.path.exists("/var/lib/dbus/machine-id"):
            run("/usr/bin/dbus-uuidgen --ensure")

        run("/sbin/start-stop-daemon -b --start --pidfile /run/dbus/pid --exec /usr/bin/dbus-daemon -- --system")
        sys.exit(0)
    wait_bus("%s/run/dbus/system_bus_socket" % output_dir)


# run command and terminate if something goes wrong
def run(cmd, ignore_error=False):
    print cmd
    ret = os.system(cmd)
    if ret and not ignore_error:
        print "%s returned %s" % (cmd, ret)
        sys.exit(1)

def create_sandbox(output_dir, repository):
    global bus

    try:
        # Add repository of the packages
        run('pisi --yes-all --destdir="%s" add-repo lime %s' % (output_dir, repository))

        run('pisi --yes-all --ignore-comar --ignore-file-conflicts --ignore-safety --ignore-dep -D"%s" it baselayout' % output_dir)
        run('pisi --yes-all --ignore-comar --ignore-file-conflicts --ignore-safety --ignore-dep -D"%s" it `cat ./list.txt`' % output_dir)

        # Create /etc from baselayout
        path = "%s/usr/share/baselayout/" % output_dir
        path2 = "%s/etc" % output_dir
        for name in os.listdir(path):
            run('cp -p "%s" "%s"' % (os.path.join(path, name), os.path.join(path2, name)))

        os.mknod("%s/dev/null" % output_dir, 0666 | stat.S_IFCHR, os.makedev(1, 3))
        os.mknod("%s/dev/console" % output_dir, 0666 | stat.S_IFCHR, os.makedev(5, 1))

        os.mknod("%s/dev/random" % output_dir, 0666 | stat.S_IFCHR, os.makedev(1, 8))   

        os.mknod("%s/dev/urandom" % output_dir, 0666 | stat.S_IFCHR, os.makedev(1, 9))

        # run command in chroot
        def chrun(cmd):
            run('chroot "%s" %s' % (output_dir, cmd))

        chrun("/sbin/ldconfig")
        chroot_comar(output_dir)
        

        chrun("/usr/bin/pisi cp baselayout")
        chrun("/usr/bin/pisi cp")

        path = os.path.join(output_dir, "usr/lib/locale")
        if not os.path.exists(path):
          os.makedirs(path)

        chrun("/bin/sed -i 's|#en_US.UTF-8 UTF-8|en_US.UTF-8 UTF-8|' etc/locale.gen")
        chrun("/usr/bin/locale-gen")

        connectToDBus(output_dir)

        obj = bus.get_object("tr.org.pardus.comar", "/package/baselayout")

        obj.setUser(0, "", "", "", "", "", dbus_interface="tr.org.pardus.comar.User.Manager")
       
        path = os.path.join(output_dir, "run/openrc")
        if not os.path.exists(path):
          os.makedirs(path)

        chrun("/bin/touch /run/openrc/softlevel")
        chrun("rm -rf /run/dbus/*")

    except KeyboardInterrupt:
        run('umount %s/proc' % output_dir, ignore_error=True)
        run('umount %s/sys' % output_dir, ignore_error=True)
        sys.exit(1)

def tarball(output_dir):
    today = datetime.date.today()

    os.chdir("%s"% output_dir)
    
    run("tar -cJf lime_%s.tar.xz *"% today) 

    run('mv lime_%s.tar.xz ../../.' % today)
   
  #  shutil.rmtree("../%s" % output_dir)
    

cmd = sys.argv[1]

if cmd == "create":
    create_sandbox("image", "/var/db/buildfarm/packages/0.5/x86_64/pisi-index.xml.xz")
    tarball("image")

elif cmd == "reset":
    umount_sandbox()


