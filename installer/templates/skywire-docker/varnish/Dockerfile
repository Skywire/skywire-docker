{% if varnish == "6" %}
FROM varnish:stable
{% elif varnish == "5" %}
FROM secoresearch/varnish
{% endif %}

LABEL com.skywire.container="Varnish"
LABEL version="0.0.1"
LABEL description="Skywire Varnish Docker container"

COPY default.vcl /etc/varnish/
