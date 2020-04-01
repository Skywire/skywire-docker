FROM php:5.6-fpm

LABEL com.skywire.container="Php-Fpm"
LABEL version="0.0.1"
LABEL description="Skywire php-fpm5.6 Docker container"

ENV	HOME /root
ENV	GOPATH $HOME/go
WORKDIR /$HOME

RUN apt-get update && apt-get install -y \
            mysql-client \
            golang-go \
            git \
            npm \
            libfreetype6-dev \
            libjpeg62-turbo-dev \
            libpng-dev \
            libxml2-dev \
            libmcrypt-dev \
            vim \
            redis-tools \
            pv \
            zsh \
            wget \
        && docker-php-ext-install -j$(nproc) gd \
        && pecl install xdebug-2.5.5 \
        && docker-php-ext-install mcrypt pdo_mysql soap intl bcmath \
        && docker-php-ext-enable opcache xdebug

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
RUN curl -sS https://getcomposer.org/installer | php \
    && mv composer.phar /usr/local/bin/composer

{% if ioncube %}
#install ioncube
RUN curl -fsSL 'https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz' -o ioncube_loaders.tar.gz \
    && mkdir -p /tmp/ioncube_loaders \
    && tar -xf ioncube_loaders.tar.gz -C /tmp/ioncube_loaders --strip-components=1 \
    && rm ioncube_loaders.tar.gz \
    && cp /tmp/ioncube_loaders/ioncube_loader_lin_5.6.so /usr/local/lib/php/extensions/no-debug-non-zts-20170718/ \
    && docker-php-ext-enable ioncube_loader_lin_5.6.so \
    && rm -r /tmp/ioncube_loaders
{% endif %}

#install ZSH
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

WORKDIR /var/www/html/