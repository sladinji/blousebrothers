FROM solr:6

RUN mkdir -p /opt/solr/server/solr/mycores

# add solr config (./manage.py build_solr_schema > schema.xml)
# Adding Files
COPY ./solr_cfg/mycore /opt/solr/server/solr/mycores/mycore
USER root
RUN mkdir -p /opt/solr/server/solr/mycores/mycore/data

# Create Core.properties

# set ownership to solr user
RUN chown -R solr:solr /opt/solr/server/solr

USER solr
