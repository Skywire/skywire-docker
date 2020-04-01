#get official docker image	
FROM elasticsearch:6.8.6	

MAINTAINER Tom Scott-Malden tom@skywire.co.uk	

LABEL com.skywire.container="ElasticSearch"	
LABEL version="0.0.1"	
LABEL description="Skywire ElasticSearch Docker container"	

RUN cd /usr/share/elasticsearch; bin/elasticsearch-plugin install analysis-phonetic; bin/elasticsearch-plugin install analysis-icu	
RUN printf '\nscript.inline: on\nscript.indexed: on' >> $ES_PATH_CONF/elasticsearch.yml 