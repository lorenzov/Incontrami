# Replace these three settings.
PROJDIR="/home/ubuntu/Incontrami/src/incontrami"
PIDFILE="$PROJDIR/mysite.pid"
SOCKET="/home/ubuntu/incontrami.sock"
export PYTHONPATH=/home/ubuntu/Incontrami/src/:/var/django/
export DJANGO_SETTINGS_MODULE=incontrami.settings
cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

exec ./manage.py runfcgi  method=threaded host=127.0.0.1 port=3035 pidfile=$PIDFILE
