groupadd tcpdump
usermod -a -G tcpdump $USER
chgrp tcpdump /usr/sbin/tcpdump
chmod 0750 /usr/sbin/tcpdump
setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
