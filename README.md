# Skywire Docker

Skywire uses docker to provide a consistent development environment across the team. This enviroment attempts to be as close a match as possible to the production environment. By doing this, we should reduce the likelyhood of issues arrising becuase of environmental factors.

## 1. Install Docker

* Install [Docker](https://www.docker.com/products/docker) to quickly and easily install and setup a Docker environments on your computer. Docker is available for Windows, Mac and Linux.
* Consider following [Performance Tuning Docker for Mac](http://markshust.com/2018/01/30/performance-tuning-docker-mac)
* NB. [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/) is no longer supported.

## 2. Install Skywire Docker Configuration Into Your Project

Clone this repository locally and run the OS specific installer from the cloned repository to install and configure settings specfic to you project:

```sh
./bin/install.mac
```

or

```sh
./bin/install.linux
```

You'll be prompted for project configuration options during the installation e.g. PHP version, M1 vs. M2

Once complete a number of new files will exist in your project which define it's Docker container configuration.

## 3. Build and Start Docker Container

* `cd` to your project's directory and run the commands below to build and start the containers:

```sh
docker-compose build
docker-compose up -d
```

* `docker-compose build` will build the services in the `docker-compose.yml` file.
* `docker-compose up` creates and starts the  containers. The `-d` flagstarts the containers in the background and leaves them running. [Kitematic](https://kitematic.com/) can then be used to view logs, ssh into a container etc.
* You will need to [update your hosts file](https://www.sonassi.com/help/general/editing-hosts-file) with the Docker IP and hostnames:

```sh
127.0.0.1 docker.XXX.YYY XXX_mysql XXX_redis XXX_elasticsearch
```

* Replace `XXX` with the Second Level Domain(SLD) and `YYY` with the Top Level Domain(TLD). `docker` is always used for consistency. So, for a production domain of `www.somehost.co.uk` the hosts entry would be:

```sh
127.0.0.1 docker.somehost.co.uk somehost_mysql somehost_redis somehost_elasticsearch
```

At this point you should have a set of running docker containers, correctly configured for your project. We still need to configure the application of your project for Docker, which is covered below.

## 4. Stopping Services

This can either be done from within the Kitematic interface or by running `docker-compose stop` from within the project's directory.

## 5. Connecting to PHP container

The PHP container has all the tools required to build and use the site locally. It contains:
* Composer
* NVM
* redis-tools
* pv
* zsh

To connect to it you can add the following alias to your `~/.bashrc` file:
~~~
de(){
    docker exec -i -t $1 zsh
}

dephp() {
    de $(docker ps | grep phpfpm | cut -c1-12);
}
~~~
Once done, you can then run `dephp` from with in the root directory of the project to open a terminal in the PHP container.

## MySQL and [n98-magerun](https://github.com/netz98/n98-magerun)

* Notice the _mysql bit, you can use the container name for the mysql container from the `docker-compose.yml` file. This is so that your local magerun can connect to the db correctly without the need for a seperate CLI docker to do so.
* Once your `local.xml` is setup, you can then run n98-magerun to import a database (you don't have to do this from within a docker container, it should work from command line (refer to the 'MySQL and n98-magerun' section for installing a MySQL client on Mac).

Connection details to connect to the Docker database:

* Host: `somehost_mysql` *db host would need to be the "container_name" of the mysql container from the docker-compose.yml*
* DB Name: `docker`
* Username: `root`
* Password: `pa55w0rd`

* Install MySQL for Mac so you have access to mysql: [http://wphosting.tv/how-to-install-mysql-on-mac-os-x-el-capitan/](http://wphosting.tv/how-to-install-mysql-on-mac-os-x-el-capitan/)
* You want mysql 5.6 or less as n98-magerun doesn't currently support 5.7 as it uses the `--pass` flag which is deprecated.
* Add the export to your `.bash_profile`.
* You now have native n98-magerun support without having to be within a container
* Sample `app/etc/local.xml`:

```xml
<host><![CDATA[somehost_mysql]]></host><!-- the "container_name" of the mysql container from the docker-compose.yml -->
<username><![CDATA[root]]></username><!-- Default root Username -->
<password><![CDATA[pa55w0rd]]></password><!-- Default root Password -->
<dbname><![CDATA[docker]]></dbname><!-- Default DB name -->
```

## [Kibana](https://www.elastic.co/guide/en/kibana/6.8)

We can use kibana to look at all the logs across the entire docker instance. It needs a little bit of setup though

* Head to [http://localhost:5601/](http://localhost:5601/)
* You'll be asked to create a new index pattern
    * Index pattern should be `filebeat-*`
    * It might be worth narrowing down the amount of logs using a query here, ie `filebeat-2020-*`
    * Click next
* Set `Time Filter field name` to `@timestamp`
* Click `Create index pattern`

## [Varnish](https://varnish-cache.org/)

Varnish is the recommended FPC for M2 and can be installed with teh `skywire-docker` installer. Once installed via docker, you can configure it by:

* https://devdocs.magento.com/guides/v2.3/config-guide/varnish/config-varnish-magento.html
* Backend host is the Nginx hostname, similar to: `somehost_nginx`
* Backend port is the Nginx port, typically port `8080`
* Add the Nginx hostname to the Access list as well.
* Generate a VCL for the appropriate varnish version following the readme above
* Rename the downloaded `varnish.vcl` to `default.vcl`
* Place the VCL file in `skywire-docker/varnish`
* Rebuild the docker image, `docker-composer build`
* Start up docker
8 You can check that varnish is running Ok by looking at the response headers

## [Redis](https://redis.io/)

* A Redis container has now been installed, mainly to be used with Magento 2
* Copy the default settings as [magento suggests](http://devdocs.magento.com/guides/v2.0/config-guide/redis/config-redis.html) and update your `app/etc/env.php` with the hostname from the `docker-compose.yml`
* If you want to access the docker Redis or use n98 on your host machine you'll need to add the network name of the container to your hosts just like mysql and the docker site.

## [ElasticSearch](https://www.elastic.co/)

* I've now added elastic search for use with M2
* Please follow details [here](https://github.com/Smile-SA/elasticsuite/wiki/ModuleInstall)
* To make this work locally you may need to create a module as described [here](https://github.com/Smile-SA/elasticsuite/wiki/ModuleInstall#optional--installing-the-module-when-using-a-custom-elasticsearch-server-location) and set the servers config value to something like ```somehost_elasticsearch:9200```
* You may only need this for installing, once installed you should be able to remove this module and configure the server in the admin.
* There is also ElasticHQ installed which you can access through something like in your browser: ```http://somehost_elasticsearch:9200/_plugin/hq/```

## [ElasticHQ](http://www.elastichq.org/)

* ElasticHQ management system is available on [http://localhost:5000](http://localhost:5000)
* The URL to connect HQ to elasticsearch is [http://elasticsearch:9200](http://elasticsearch:9200)

## [Mailhog](https://github.com/mailhog/MailHog)

* I've now installed Mailhog. PHP is all setup to use it. Just make sure to turn on emails in the admin and Mailhog will catch any outgoing emails from PHP. All you need to do is open up hostname:8025 OR [this link](http://localhost:8025)

## [Mutagen](https://mutagen.io/)

We've now setup the site to use mutagen for local development. Install from their site: [https://mutagen.io/documentation/introduction/installation/](https://mutagen.io/documentation/introduction/installation/)

1. Use `mutagen project start` to start the sync process
1. Use `mutagen project list` to see the state of the sync
   1. First sync takes a few minutes to complete.
   1. It's then checking every 10 seconds for updates to sync
1. You then bring down the syncing with `mutagen project terminate`
1. More details here: [https://mutagen.io/documentation/orchestration/](https://mutagen.io/documentation/orchestration/)


## [Blackfire](https://blackfire.io/)

Enter the shiny new performance profiler. To use blackfire, first signup for at least a hacker account [here](https://blackfire.io/signup). Once you have your account and can login, head to the [credentials page](https://blackfire.io/my/settings/credentials) where you'll find your server credentials.
1. In the root of the project, create a `.env` file
1. Add `.env` to the `.gitignore` file
1. Add the follwoing into this file:
~~~
BLACKFIRE_SERVER_ID=<Server ID>
BLACKFIRE_SERVER_TOKEN=<Server Token>
~~~
1. Now install the Chrome or Firefox plugin from [here](https://blackfire.io/docs/integrations/browsers/index)
1. `docker-composer up -d` the project
1. Navigate to a page, and click on the plugin to profile


## XDebug

### Mac

To get XDebug running on mac.

* First, use this gist: [https://gist.github.com/ralphschindler/535dc5916ccbd06f53c1b0ee5a868c93](https://gist.github.com/ralphschindler/535dc5916ccbd06f53c1b0ee5a868c93)
* Next, update the skywire_updates.ini file you find in the php/src folder.

From:

```ini
xdebug.remote_connect_back = 1
xdebug.remote_host = 192.168.99.1
;xdebug.remote_connect_back = 0
;xdebug.remote_host = 10.254.254.254
```

To:

```ini
;xdebug.remote_connect_back = 1
;xdebug.remote_host = 192.168.99.1
xdebug.remote_connect_back = 0
xdebug.remote_host = 10.254.254.254
```

### Windows

On Windows Docker will create a network interface with an IP, this is what you need to set your xdebug.remote_host to in PHP-FPM skywire_updates.ini file

The default IP should 10.0.75.1, you can check this from the docker for windows settings (found in your system tray)

You may also need to allow port 9000 through on the windows firewall, this is an exercise left to the reader.

## Building The Installation Binaries

To rebuild the installation binaries from source you will need:

* Python 2.7+
* pip

The following commends will generate an install binary in `bin`:

```sh
sudo pip install -r requirements.txt
pyinstaller --onefile --distpath bin install.py
```

### macOS Python/pip3 Installation

Assuming you have [homebrew](https://brew.sh/) installed, use it to obtain the latest version of Python:

```sh
brew install python
```

`pip3` is also installed with this, so use that to install other dependencies which are listed in the `requirements.txt`:

```sh
sudo pip3 install -r requirements.txt
```

## Troubleshooting

### Issue

404's and `Cannot create a symlink for ...` with Windows and Magento 2

### Solution

In `app/etc/di.xml` change:

```xml
<item name="view_preprocessed" xsi:type="object">Magento\Framework\App\View\Asset\MaterializationStrategy\Symlink</item>
```

to

```xml
<item name="view_preprocessed" xsi:type="object">Magento\Framework\App\View\Asset\MaterializationStrategy\Copy</item>
```

**Do not commit the change.**

### Issue:

`(Exception): Warning: SessionHandler::read()`

### Solution:

    create var/session
    chmod -R 777 var

### Issue:

`Magento\Framework\Exception\LocalizedException): The configuration file has changed. Run app:config:import or setup:upgrade command to synchronize configuration.`

### Solution:

From container

    php bin/magento setup:upgrade
    
### Issue:

mysql container shutting down after starting with error:
    `2018-10-29 16:54:54 7f8698032740  InnoDB: Operating system error number 13 in a file operation.
    InnoDB: The error means mysqld does not have the access rights to
    InnoDB: the directory.`
    
### Solution:

skywire-docker/data doesn't have correct permissions, run:
    `chmod -R 777 skywire-docker/data`
    
### Issue:

`RuntimeException: Can't create directory /var/www/html/generated/code/Magento/Framework/App/Http/. Class Magento\Framework\App\Http\Interceptor generation error: The requested class did not generate properly, because the 'generated' directory permission is read-only`

### Solution:

`chmod -R 777 generated`
    
### Issue:

No alive nodes found in your cluster

### Solution:

Check the `core_config_data` table in your local database, more specifically the `smile_elasticsuite_core_base_settings/es_client/servers` config path. That should be pointing to `somehost_elasticsearch:9200` and not `localhost`.  Check that the `somehost_elasticsearch` container is running, it might have errored on startup because of insufficient rights to write to `skywire-docker/data/elasticsearch/data` - change permissions using `chmod 777 skywire-docker/data/elasticsearch/data`

If the issue persists, flush the caches via `php bin/magento cache:flush` and reindex via `php bin/magento index:reindex`

### Issue:

`catalog_product` index does not exist yet. Make sure everything is reindexed

### Solution:

If you keep getting `catalog_product index does not exist yet. Make sure everything is reindexed.` with `Smile_ElasticSearch` then check if `catalogsearch_fulltext` indexer has stalled. If so, run `php bin/magento indexer:reset catalogsearch_fulltext && php -d memory_limit=2G bin/magento indexer:reindex catalogsearch_fulltext`

### Issue:

`Catalog Search indexer process unknown error`

### Solution:

`Catalog Search indexer process unknown error:
{"error":{"root_cause":[{"type":"mapper_parsing_exception","reason":"No handler for type [text] declared on field [search]"}],"type":"mapper_parsing_exception","reason":"No handler for type [text] declared on field [search]"},"status":400}`

You are using an older version of either one of the elastic modules or the docker container.
