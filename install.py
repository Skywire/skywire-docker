# Import necessary functions from Jinja2 module
from jinja2 import Environment, FileSystemLoader
import click
from git import Repo
import sys
from os import path
from distutils import dir_util, file_util


@click.command()
@click.option('--install-path', prompt="Install Path? (absolute path, no trailing slash)",
              help="Directory to install to", required=True)
@click.option('--domain', prompt="The domain name to use without a subdomain e.g. example.com",
              help="Domain name to use", required=True)
@click.option('--mage', prompt="Magento Version", type=click.Choice(["1", "2"]), help="Magento Version", required=True, default="2")
@click.option('--php', prompt="Php Version", type=click.Choice(["54", "5.4", "55", "5.5", "56" , "5.6", "70", "7.0", "71", "7.1", "72","7.2", "73","7.3"]), help="Php Version", required=True, default="73")
@click.option('--http2/--no-http2', prompt="Use Http2?", help="Use Http2", required=True, is_flag=True, default=True)
@click.option('--varnish', prompt="Use Varnish (Version 5 or 6, 0 for none)?", type=click.Choice(["5", "6", "0"]), help="Use Varnish", required=True, default="0")
@click.option('--redis/--no-redis', prompt="Use Redis?", help="Use Redis", required=True, is_flag=True, default=False)
@click.option('--rabbitmq/--no-rabbitmq', prompt="Use RabbitMQ?", help="Use RabbitMQ", required=True, is_flag=True, default=False)
@click.option('--mutagen/--no-mutagen', prompt="Use Mutagen?", help="Use Mutagen", required=True, is_flag=True,
              default=False)
@click.option('--ioncube/--no-ioncube', prompt="Use IonCube?", help="Use IonCube", required=True, is_flag=True,
              default=False)
@click.option('--dbpass', prompt="MySQL password (will use 'pa55w0rd' as default if not provided)",
              help="MySQL Password", required=False, default="")
@click.option('--database', prompt="MySQL database name (will use 'docker' as default if not provided)",
              help="MySQL Database", required=False, default="")
def install(install_path, domain, mage, php, http2, varnish, redis, rabbitmq, mutagen, ioncube, dbpass, database):

    click.echo("Installing skywire-docker")
    click.echo("Pulling latest version of skywire-docker from GitHub")
    git_update()

    php = php.replace(".", "")

    hostname = 'docker.' + domain
    container_prefix = domain.split(".")[0]

    click.echo("Generate nginx Dockerfile")
    handle_template("nginx/Dockerfile", {"hostname": hostname})

    click.echo("Generate nginx config for Magento {}".format(mage))
    nginx_template = "template.conf" if int(mage) == 1 else "template.conf.magento2"
    handle_template(
        "nginx/src/" + nginx_template,
        {"hostname": hostname, "container_prefix": container_prefix, 'http2': http2, "varnish": varnish},
        dest="nginx/src/template.conf"
    )

    click.echo("Generate docker-compose")
    handle_template(
        "docker-compose.yml",
        {
            "hostname": hostname,
            "container_prefix": container_prefix,
            "php": php,
            "redis": redis,
            "varnish": varnish,
            "rabbitmq": rabbitmq,
            "mutagen": mutagen,
            "dbpass": dbpass if dbpass else "pa55w0rd",
            "database": database if database else "docker"
        },
        "",
        "./../docker-compose.yml"
    )

    handle_template(
        "filebeat.docker.yml",
        {
            "container_prefix": container_prefix
        }
    )

    handle_template(
        "kibana.yml",
        {
            "container_prefix": container_prefix
        }
    )

    if int(mage) == 2 and mutagen:
        click.echo("Generate Mutagen conf");
        handle_template(
                "mutagen.yml",
                {
                    "container_prefix": container_prefix
                },
                "",
                "./../mutagen.yml"
            )

    if int(mage) == 1 and mutagen:
        click.echo("Generate Mutagen conf M1");
        handle_template(
                "mutagen.yml.m1",
                {
                    "container_prefix": container_prefix
                },
                "",
                "./../mutagen.yml"
            )

    if int(varnish) > 0:
        click.echo("Creating varnish config");
        handle_template("varnish/Dockerfile", {"varnish": varnish})

    click.echo("Generate php-fpm config");
    fpm_updated = "php-fpm/{}/src/skywire_updates.ini".format(php)
    handle_template(fpm_updated, {"container_prefix": container_prefix, "mutagen": mutagen})

    fpm_dockerfile = "php-fpm/{}/Dockerfile".format(php)
    handle_template(fpm_dockerfile, {"ioncube": ioncube, "mage": int(mage)})

    click.echo("Copying configured docker files to install path");
    copy_docker_files(install_path, mutagen)

    click.echo("Copying reamme over");
    copy_readme(install_path)

    click.echo("Cleaning up temporary files in skywire-docker")
    git_clean()

def git_update():
    repo = Repo((path.dirname(__file__)))
    remote = repo.remote('origin')
    remote.pull("master")

def git_clean():
    repo = Repo((path.dirname(__file__)))
    git = repo.git
    git.clean(["-fd","skywire-docker"])

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


def copy_docker_files(install_path, mutagen):
    dir_util.copy_tree('skywire-docker', install_path + '/skywire-docker', False)
    file_util.copy_file('docker-compose.yml', install_path + "/docker-compose.yml")
    #file_util.copy_file('README.md', install_path + "/skywire-docker/README.md")
    if mutagen:
        file_util.copy_file('mutagen.yml', install_path + "/mutagen.yml")

def copy_readme(install_path):
    f = open(install_path + '/README.md', 'a')
    f.write(open('README.md').read())


env = Environment(loader=FileSystemLoader('./installer/templates'))

install(sys.argv[1:])
