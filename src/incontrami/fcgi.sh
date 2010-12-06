# Replace these three settings.
PROJDIR="/home/ubuntu/incontrami/src/incontrami"
PIDFILE="$PROJDIR/mysite.pid"
SOCKET="/home/ubuntu/incontrami.sock"
export PYTHONPATH=/home/ubuntu/incontrami/src/:/var/django/
export DJANGO_SETTINGS_MODULE=incontrami.settings
cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

exec ./manage.py runfcgi  method=threaded host=127.0.0.1 port=3035 pidfile=$PIDFILE
