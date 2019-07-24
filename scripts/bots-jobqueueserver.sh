#! /bin/sh
#
# uses 'start-stop-daemon' , which is used in debian/ubuntu
#
#~ PATH=/sbin:/usr/sbin:/bin:/usr/bin
DEVDIR="/home/hje/Bots/botsdev/"
NAME=bots-jobqueueserver
PIDFILE=$DEVDIR$NAME"_dev.pid"
DAEMON="/usr/bin/python2.7"
DAEMON_ARGS=$DEVDIR"bots-jobqueueserver.py"

case "$1" in
    start)
        echo "Starting "$NAME" "
        start-stop-daemon --start --verbose --background --pidfile $PIDFILE --make-pidfile --startas $DAEMON -- $DAEMON_ARGS
        ;;
    stop)
        echo "Stopping "$NAME" "
        start-stop-daemon --stop --verbose --pidfile $PIDFILE
        rm -f $PIDFILE
        ;;
    restart)
        echo "Restarting "$NAME" "
        start-stop-daemon --stop --verbose --pidfile $PIDFILE
        rm -f $PIDFILE
        sleep 1
        start-stop-daemon --start --verbose --background --pidfile $PIDFILE --make-pidfile --startas $DAEMON -- $DAEMON_ARGS
        ;;
    *)
        echo "Usage: ""$(basename "$0")"" {start|stop|restart}"
        echo "    Starts the bots jobqueueserver as a daemon."
        echo "    Bots-jobqueueserver is part of bots open source edi translator (http://bots.sourceforge.net)."
        exit 1
        ;;
esac

exit 0
