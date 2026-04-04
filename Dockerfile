FROM odoo:17.0

USER root
RUN chown -R odoo:odoo /var/lib/odoo && chmod -R 755 /var/lib/odoo

COPY ./odoo.conf /etc/odoo/odoo.conf

USER odoo
