# إعدادات Gunicorn للإنتاج

# عدد العمليات
workers = 4
worker_class = "sync"
worker_connections = 1000

# إعدادات الشبكة
bind = "127.0.0.1:5000"
backlog = 2048

# إعدادات الأمان
user = "www-data"
group = "www-data"
umask = 0

# إعدادات الأداء
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2

# إعدادات التسجيل
loglevel = "info"
accesslog = "/var/log/nuzum/access.log"
errorlog = "/var/log/nuzum/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# إعدادات الذاكرة
worker_tmp_dir = "/dev/shm"

# إعدادات إعادة التشغيل
reload = False
reload_engine = "auto"

# إعدادات SSL (إذا لزم الأمر)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

def when_ready(server):
    server.log.info("خادم نُظم جاهز للعمل")

def worker_int(worker):
    worker.log.info("العامل %s: تم استلام إشارة المقاطعة", worker.pid)

def pre_fork(server, worker):
    server.log.info("العامل %s: تم إنتاجه", worker.pid)

def post_fork(server, worker):
    server.log.info("العامل %s: بدأ العمل", worker.pid)

def worker_abort(worker):
    worker.log.info("العامل %s: تم إنهاؤه", worker.pid)