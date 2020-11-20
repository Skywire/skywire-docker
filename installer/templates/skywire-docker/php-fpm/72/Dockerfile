FROM php:7.2-fpm

LABEL com.skywire.container="Php-Fpm"
LABEL version="0.0.1"
LABEL description="Skywire php-fpm7.2 Docker container"

ENV	HOME /root
ENV	GOPATH $HOME/go
WORKDIR /$HOME

RUN apt-get update && apt-get install -y \
            default-mysql-client \
            golang-go \
            git \
            npm \
            libfreetype6-dev \
            libjpeg62-turbo-dev \
            libpng-dev \
            libxml2-dev \
            libmcrypt-dev \
            libxslt-dev \
            vim \
            redis-tools \
            pv \
            zsh \
            wget \
        && docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/\
        && docker-php-ext-install -j$(nproc) gd \
        && pecl install {% if xdebug %}xdebug-2.8.0{% endif %} mcrypt-1.0.1 \
        && docker-php-ext-install pdo_mysql soap intl bcmath xsl zip sockets \
        && docker-php-ext-enable opcache {% if xdebug %}xdebug{% endif %} mcrypt

RUN version=$(php -r "echo PHP_MAJOR_VERSION.PHP_MINOR_VERSION;") \
    && curl -A "Docker" -o /tmp/blackfire-probe.tar.gz -D - -L -s https://blackfire.io/api/v1/releases/probe/php/linux/amd64/$version \
    && mkdir -p /tmp/blackfire \
    && tar zxpf /tmp/blackfire-probe.tar.gz -C /tmp/blackfire \
    && mv /tmp/blackfire/blackfire-*.so $(php -r "echo ini_get ('extension_dir');")/blackfire.so \
    && printf "extension=blackfire.so\nblackfire.agent_socket=tcp://blackfire:8707\n" > $PHP_INI_DIR/conf.d/blackfire.ini \
    && rm -rf /tmp/blackfire /tmp/blackfire-probe.tar.gz

#install NVM
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.1/install.sh | bash

RUN go get github.com/mailhog/mhsendmail
RUN mv $GOPATH/bin/mhsendmail /usr/local/bin/

RUN mv "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"

COPY src/skywire_updates.ini $PHP_INI_DIR/conf.d/

RUN sed -e 's/9000/9001/' \
        -i /usr/local/etc/php-fpm.d/zz-docker.conf

#Install grunt globally
RUN npm install grunt -g

#Install n98 magerun tools
{% if mage == 1 %}
RUN curl -L -o n98-magerun.phar https://files.magerun.net/n98-magerun.phar \
    && chmod +x ./n98-magerun.phar \
    && mv ./n98-magerun.phar /usr/local/bin/
{% endif %}

{% if mage == 2 %}
RUN curl -O https://files.magerun.net/n98-magerun2.phar \
    && chmod +x ./n98-magerun2.phar \
    && mv ./n98-magerun2.phar /usr/local/bin/
{% endif %}

#Install composer
RUN curl -sS https://getcomposer.org/installer | php -- --1  \
    && mv composer.phar /usr/local/bin/composer

# Install Prestissimo composer plugin for parallel composer downloads
RUN composer global require hirak/prestissimo

{% if ioncube %}
#install ioncube
RUN curl -fsSL 'https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz' -o ioncube_loaders.tar.gz \
    && mkdir -p /tmp/ioncube_loaders \
    && tar -xf ioncube_loaders.tar.gz -C /tmp/ioncube_loaders --strip-components=1 \
    && rm ioncube_loaders.tar.gz \
    && cp /tmp/ioncube_loaders/ioncube_loader_lin_7.2.so /usr/local/lib/php/extensions/no-debug-non-zts-20170718/ \
    && docker-php-ext-enable ioncube_loader_lin_7.2.so \
    && rm -r /tmp/ioncube_loaders
{% endif %}

#install ZSH
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

WORKDIR /var/www/html/