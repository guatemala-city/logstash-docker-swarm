ARG SRC_IMAGE_VER
FROM guatemalacityex/logstash:$SRC_IMAGE_VER

ARG LS_JAVA_OPTS
ENV LS_JAVA_OPTS=$LS_JAVA_OPTS


ARG JENKINS_URL
ARG NODE_NAME
ARG JOB_NAME
ARG BRANCH_NAME
ARG COMMIT_ID
ARG BUILD_ID

LABEL jenkins.url="${JENKINS_URL}"
LABEL node.name="${NODE_NAME}"
LABEL job.name="${JOB_NAME}"
LABEL branch.name="${BRANCH_NAME}"
LABEL commit.id="${COMMIT_ID}"
LABEL build.id="${BUILD_ID}"

USER root

COPY pipeline.conf /usr/share/logstash/pipeline/pipeline.conf
RUN chown --recursive logstash:logstash /usr/share/logstash/config/

COPY ./healthcheck.sh /healthcheck.sh
RUN chmod +x /healthcheck.sh

USER logstash

HEALTHCHECK --interval=20s --timeout=10s --retries=6 CMD /healthcheck.sh

CMD ["logstash","-f","/usr/share/logstash/pipeline/pipeline.conf"]
