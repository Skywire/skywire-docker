# Import necessary functions from Jinja2 module
from jinja2 import Environment, FileSystemLoader
import click
import sys
from os import path
from distutils import dir_util, file_util


@click.command()
@click.option('--install-path', prompt="Install Path? (absolute path, no trailing slash)",
              help="Directory to install to", required=True)
@click.option('--domain', prompt="The domain name to use without a subdomain e.g. example.com",
              help="Domain name to use", required=True)
@click.option('--framework', prompt="Which Framework", type=click.Choice(["magento2", "wordpress"]), help="Choose which framework is required", required=True, default="magento2")
@click.option('--php', prompt="Php Version", type=click.Choice(["71", "7.1", "72","7.2", "73","7.3", "74","7.4"]), help="Php Version", required=True, default="73")
@click.option('--varnish', prompt="Use Varnish (Version 5 or 6, 0 for none)?", type=click.Choice(["5", "6", "0"]), help="Use Varnish", required=True, default="0")
@click.option('--redis/--no-redis', prompt="Use Redis?", help="Use Redis", required=True, is_flag=True, default=False)
@click.option('--rabbitmq/--no-rabbitmq', prompt="Use RabbitMQ?", help="Use RabbitMQ", required=True, is_flag=True, default=False)
@click.option('--elasticsearch/--no-elasticsearch', prompt="User elasticsearch?", help="User elasticsearch?", required=True, is_flag=True, default=False)
@click.option('--ioncube/--no-ioncube', prompt="Use IonCube?", help="Use IonCube", required=True, is_flag=True,
              default=False)
@click.option('--xdebug/--no-xdebug', prompt="Use xdebug?", help="Use xdebug", required=True, is_flag=True,
              default=False)
@click.option('--dbpass', prompt="MySQL password (will use 'pa55w0rd' as default if not provided)",
              help="MySQL Password", required=False, default="")
@click.option('--database', prompt="MySQL database name (will use 'docker' as default if not provided)",
              help="MySQL Database", required=False, default="")
def install(install_path, domain, framework, php, varnish, redis, rabbitmq, elasticsearch, ioncube, xdebug, dbpass, database):

    click.echo("Installing skywire-docker")

    php = php.replace(".", "")
    phpDot = php[:1] + '.' + php[1:]

    hostname = 'docker.' + domain
    container_prefix = domain.split(".")[0]

    click.echo("Generate nginx Dockerfile")
    handle_template("nginx/Dockerfile", {"hostname": hostname})

    click.echo("Generate nginx config for {}".format(framework))
    nginx_template = "template.conf.wordpress" if framework == 'wordpress' else "template.conf.magento2"
    handle_template(
        "nginx/src/" + nginx_template,
        {"hostname": hostname, "container_prefix": container_prefix, "varnish": varnish},
        dest="nginx/src/template.conf"
    )

    click.echo("Generate docker-compose")
    handle_template(
        "docker-compose.yml",
        {
            "hostname": hostname,
            "container_prefix": container_prefix,
            "php": php,
            "xdebug": xdebug,
            "redis": redis,
            "varnish": varnish,
            "rabbitmq": rabbitmq,
            "dbpass": dbpass if dbpass else "pa55w0rd",
            "database": database if database else "docker",
            'elasticsearch': elasticsearch
        },
        "",
        "./../docker-compose.yml"
    )

    click.echo("Generate makefile")
    handle_template(
        "makefile",
        {},
        "",
        "./../makefile"
    )

    if int(varnish) > 0:
        click.echo("Creating varnish config");
        handle_template("varnish/Dockerfile", {"varnish": varnish})

    click.echo("Generate php-fpm config");
    handle_template("php-fpm/src/skywire_updates.ini", {"container_prefix": container_prefix})
    handle_template("php-fpm/src/skywire_updates_xdebug2.ini", {"container_prefix": container_prefix})
    handle_template("php-fpm/src/skywire_updates_xdebug3.ini", {"container_prefix": container_prefix})
    handle_template("php-fpm/Dockerfile", {"ioncube": ioncube, "framework": framework, "phpDot": phpDot})

    click.echo("Copying configured docker files to install path");
    copy_docker_files(install_path)

    click.echo("Copying readme over");
    copy_readme(install_path)

    click.echo("Cleaning up temporary files in skywire-docker")


def handle_template(name, args, template_dir="skywire-docker/", dest=None):
    """
    Load and render a template with the provided args,
    then copy to the skywire-docker destination
    """
    template = env.get_template(template_dir + name)
    rendered = template.render(args)

    output_path = "skywire-docker/" + name if not dest else "skywire-docker/" + dest

    file = open(output_path, "w")
    file.writelines(rendered)


def copy_docker_files(install_path):
    dir_util.copy_tree('skywire-docker', install_path + '/skywire-docker', False)
    file_util.copy_file('docker-compose.yml', install_path + "/docker-compose.yml")
    file_util.copy_file('makefile', install_path + "/makefile")
    #file_util.copy_file('README.md', install_path + "/skywire-docker/README.md")

def copy_readme(install_path):
    f = open(install_path + '/README.md', 'a')
    f.write(open('README.md').read())


env = Environment(loader=FileSystemLoader('./installer/templates'))

install(sys.argv[1:])
