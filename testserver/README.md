# Test server

You need to install nginx >= 1.9.5 to have support of both HTTP/1 and HTTP/2.

Also, to run tcpdump without being root, run `tcpdump_as_non_root.sh` to create the tcpdump group. If your current user is not added, try executing `sudo usermod -a -G tcpdump your_user` and log out/log in to take this into account.

**TODO: the running user of celery server should be a user called tcpdump (not yet implemented)**

The server must be run as root, i.e.

```bash
sudo python3 manage.py runserver
```

But the celery daemon **should not** (for security reasons).
```bash
python3 manage.py celeryd
```
