FROM php:{{ phpDot }}-fpm AS php_base

LABEL com.skywire.container="Php-Fpm"
LABEL version="1.0.0"
LABEL description="Skywire php-fpm{{ container_prefix }} Docker container"

ENV	HOME /root
WORKDIR /$HOME

RUN apt-get update && apt-get install -y \
            default-mysql-client \
            git \
            nodejs \
            npm \
            libfreetype6-dev \
            libjpeg62-turbo-dev \
            libpng-dev \
            libxml2-dev \
            libmcrypt-dev \
            libxslt-dev \
            libzip-dev \
            vim \
            redis-tools \
            pv \
            sendmail \
            wget

RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
        && docker-php-ext-install -j$(nproc) gd \
        && pecl install mcrypt \
        && docker-php-ext-install {% if framework == 'wordpress' %}mysqli{% endif %} pdo_mysql soap intl bcmath xsl zip sockets \
        && docker-php-ext-enable opcache mcrypt

#install NVM
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.1/install.sh | bash

RUN mv "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"

COPY src/skywire_updates.ini $PHP_INI_DIR/conf.d/

RUN sed -e 's/9000/9001/' \
        -i /usr/local/etc/php-fpm.d/zz-docker.conf
        
#Install grunt globally
RUN npm install grunt -g


{% if framework == 'wordpress' %} \
#Install wp cli
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x ./wp-cli.phar \
    && mv ./wp-cli.phar /usr/local/bin/
{% else %} \
#Install n98 magerun tools
RUN curl -O https://files.magerun.net/n98-magerun2.phar \
    && chmod +x ./n98-magerun2.phar \
    && mv ./n98-magerun2.phar /usr/local/bin/
{% endif %}

#Install composer
RUN curl -sS https://getcomposer.org/installer | php -- --2  \
    && mv composer.phar /usr/local/bin/composer

{% if ioncube %}
#install ioncube
RUN curl -fsSL 'https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz' -o ioncube_loaders.tar.gz \
    && mkdir -p /tmp/ioncube_loaders \
    && tar -xf ioncube_loaders.tar.gz -C /tmp/ioncube_loaders --strip-components=1 \
    && rm ioncube_loaders.tar.gz \
    && cp /tmp/ioncube_loaders/ioncube_loader_lin_{phpDot}.so /usr/local/lib/php/extensions/no-debug-non-zts-20180731/ \
    && docker-php-ext-enable ioncube_loader_lin_{phpDot}.so \
    && rm -r /tmp/ioncube_loaders
{% endif %}

WORKDIR /var/www/html/

ARG USER_ID
ARG GROUP_ID
ARG USERNAME

RUN getent group $GROUP_ID || addgroup --gid $GROUP_ID $USERNAME
RUN adduser --disabled-password  --gecos '' --uid $USER_ID --gid $GROUP_ID $USERNAME
USER $USERNAME

ENV HOME /home/$USERNAME

FROM php_base AS php_xdebug

USER root

RUN pecl install xdebug \
        && docker-php-ext-enable xdebug

RUN sed -e 's/9001/9002/' \
        -i /usr/local/etc/php-fpm.d/zz-docker.conf

COPY src/skywire_updates_xdebug3.ini $PHP_INI_DIR/conf.d/

USER $USERNAME
