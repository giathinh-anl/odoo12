# Sử dụng image chính thức của Odoo (bạn có thể đổi 17.0 thành bản bạn muốn)
FROM odoo:17.0

# Copy file cấu hình vào container
COPY ./odoo.conf /etc/odoo/odoo.conf

# (Tùy chọn) Copy thư mục chứa các module tùy chỉnh
# COPY ./custom_addons /mnt/extra-addons