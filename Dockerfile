FROM odoo:17.0

USER root

RUN chmod 777 /var/lib/odoo

COPY ./odoo.conf /etc/odoo/odoo.conf
COPY ./addons /mnt/extra-addons

ENTRYPOINT ["/bin/bash", "-c", "chmod -R 777 /var/lib/odoo && exec /entrypoint.sh odoo"]