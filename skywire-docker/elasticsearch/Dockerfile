#get official docker image	
FROM docker.elastic.co/elasticsearch/elasticsearch:7.17.9

MAINTAINER Tom Scott-Malden tom@skywire.co.uk	

LABEL com.skywire.container="ElasticSearch"	
LABEL version="0.0.2"
LABEL description="Skywire ElasticSearch Docker container"	

RUN cd /usr/share/elasticsearch; bin/elasticsearch-plugin install analysis-phonetic;