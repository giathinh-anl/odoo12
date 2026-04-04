FROM odoo:17.0

USER root
RUN mkdir -p /var/lib/odoo && chmod -R 777 /var/lib/odoo

COPY ./odoo.conf /etc/odoo/odoo.conf

USER odoo
