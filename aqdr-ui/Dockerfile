# Copyright © 2021-2026 Bull SAS
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of work done in the K-HEALTHinAIR EU funded project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# https://hub.docker.com/r/grafana/grafana-oss/tags
# docker build --no-cache --progress=plain -t khealthinair/aqdr-ui:latest .
FROM grafana/grafana-oss:11.4.0
LABEL version="2.0.0" maintainer="Alberto Acebes <alberto.acebes@eviden.com>"

##################################################################
## CONFIGURATION, some could be overrited via aqdr-ui-config ConfigMap
##################################################################
ENV GF_LOG_LEVEL=info
ENV GF_ENABLE_GZIP=true
ENV GF_USERS_DEFAULT_THEME=light
ENV GF_AUTH_BASIC_ENABLED=true
ENV GF_AUTO_ASSIGN_ORG=true
ENV GF_AUTO_ASSIGN_ORG_ID=1
ENV GF_AUTO_ASSIGN_ORG_ROLE=Viewer
ENV GF_DEFAULT_WEEK_START=monday
ENV GF_ALERTING_ENABLED=false
ENV GF_UNIFIED_ALERTING_ENABLED=false
ENV GF_EXPLORE_ENABLED=false
ENV GF_ANALYTICS_CHECK_FOR_UPDATES=false
ENV GF_ANALYTICS_CHECK_FOR_PLUGIN_UPDATES=false
ENV GF_PATHS_PLUGINS="/var/lib/grafana/plugins"
ENV GF_PATHS_PROVISIONING="/etc/grafana/provisioning"
ENV GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH="/etc/grafana/provisioning/dashboards/default/0.home-page.json"
ENV GF_PANELS_DISABLE_SANITIZE_HTML=true
ENV GF_FEATURE_TOGGLES_ENABLE="panelTitleSearch,formatString,pdfTables"
ENV GF_AUTH_ANONYMOUS_ENABLED=false
ENV GF_AUTH_ANONYMOUS_ORG_NAME=K-HEALTHinAIR
ENV GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
ENV GF_AUTH_ANONYMOUS_HIDE_VERSION=true

##################################################################
## K-HEALTHinAIR Customization
##################################################################
USER root
RUN echo "Current user to perform modifications is: $(whoami)"
# COPY conf/grafana.ini /etc/grafana/grafana.ini

## VISUAL resources: icons, logos and backgrounds
COPY --chown=grafana:grafana grafana-customization/fonts/*.woff2 /usr/share/grafana/public/fonts
COPY --chown=grafana:grafana grafana-customization/img/* /usr/share/grafana/public/img
COPY --chown=grafana:grafana grafana-customization/img/fav32.png /usr/share/grafana/public/img/apple-touch-icon.png

##################################################################
## PROVISIONING, datasource and dashboards
##################################################################
COPY --chown=grafana:grafana conf/provisioning/datasources /etc/grafana/provisioning/datasources
COPY --chown=grafana:grafana conf/provisioning/dashboards /etc/grafana/provisioning/dashboards
#COPY conf/provisioning/access-control /etc/grafana/provisioning/access-control

##################################################################
## Changes in texts in views
## Depends on source code, so on the specific grafana version !!
##################################################################
## Update Title
RUN sed -i 's|<title>\[\[.AppTitle\]\]</title>|<title>K-HEALTHinAIR AQDR</title>|g' /usr/share/grafana/public/views/index.html
RUN sed -i 's|Loading Grafana|Loading K-HEALTHinAIR AQDR|g' /usr/share/grafana/public/views/index.html
RUN sed -i 's|<body>|<body style=\"background-image: url('\[\[.ContentDeliveryURL\]\]public/img/Header_Home_si.png');\">|g' /usr/share/grafana/public/views/index.html
RUN find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|AppTitle="Grafana"|AppTitle="K-HEALTHinAIR AQDR"|g' {} \;
RUN find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|LoginTitle="Welcome to Grafana"|LoginTitle="K-HEALTHinAIR Platform AQDR"|g' {} \;

## Update Help menu
RUN sed -i "s|\[\[.NavTree\]\],|nav,|g; \
    s|window.grafanaBootData = {| \
    let nav = [[.NavTree]]; \
    const alerting = nav.find((element) => element.id === 'alerting'); \
    if (alerting) { alerting['url'] = '/alerting/list'; } \
    # const dashboards = nav.find((element) => element.id === 'dashboards/browse'); \
    # if (dashboards) { dashboards['children'] = [];} \
    const connections = nav.find((element) => element.id === 'connections'); \
    if (connections) { connections['url'] = '/datasources'; connections['children'].shift(); } \
    const help = nav.find((element) => element.id === 'help'); \
    if (help) { help['subTitle'] = 'Grafana OSS'; help['children'] = [];} \
    window.grafanaBootData = {|g" \
    /usr/share/grafana/public/views/index.html

## Remove Documentation, Support, Community, Edition, Version and New Version in the Footer
## And add Public Acess aligned with GF_AUTH_ANONYMOUS_ENABLED
RUN if [ "$GF_AUTH_ANONYMOUS_ENABLED" = "true" ]; then \
    echo "Enabling Public access due to GF_AUTH_ANONYMOUS_ENABLED value..."; \
    find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|\[{target:"_blank",id:"documentation".*grafana_footer"}\]|\[{target:"_self",id:"public",text:"PUBLIC ACCESS",icon:"chart-line",url:"/"}\]|g' {} \;; \
    else \
    find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|\[{target:"_blank",id:"documentation".*grafana_footer"}\]|\[\]|g' {} \;; \
    fi

## Remove News and Open Source icons
RUN find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|..createElement(....,{className:.,onClick:.,iconOnly:!0,icon:"rss","aria-label":"News"})|null|g' {} \;
RUN find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|.push({target:"_blank",id:"version",text:`${..edition}${.}`,url:..licenseUrl,icon:"external-link-alt"})||g' {} \;

## Login Public Access footer link style
RUN find /usr/share/grafana/public/build/ -name *.css -exec sed -i 's|.footer{font-size:12px;|.footer{font-size:20px;font-weight:bold;|g' {} \;
RUN find /usr/share/grafana/public/build/ -name *.css -exec sed -i 's|.login-page .footer a{color:#24292e}.login-page|.login-page .footer a{color:#548343}.login-page|g' {} \;

## Customize the reset password email
RUN sed -i 's|Reset your Grafana password|Reset your K-HEALTHinAIR Platform AQDR password|g' /usr/share/grafana/public/emails/reset_password.html
RUN sed -i 's|https://grafana.com/static/assets/img/logo_new_transparent_light_400x100.png|https://aqdr.k-healthinair.ari-health.eu/public/img/K-HEALTHinAIR_original@3x.png|g' /usr/share/grafana/public/emails/reset_password.html
RUN sed -i 's|>&copy;.*</a>.<|><a href="https://k-healthinair.eu/" style="color: #6E9FFF;">K-HEALTHinAIR</a><|g' /usr/share/grafana/public/emails/reset_password.html

##################################################################
## CLEANING Remove Native Data Sources
##################################################################
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/elasticsearch
RUN rm -rf /usr/share/grafana/public/build/elasticsearch*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/graphite
RUN rm -rf /usr/share/grafana/public/build/graphite*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/opentsdb
RUN rm -rf /usr/share/grafana/public/build/opentsdb*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/mssql
RUN rm -rf /usr/share/grafana/public/build/mssql*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/mysql
RUN rm -rf /usr/share/grafana/public/build/mysql*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/tempo
RUN rm -rf /usr/share/grafana/public/build/tempo*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/jaeger
RUN rm -rf /usr/share/grafana/public/build/jaeger*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/zipkin
RUN rm -rf /usr/share/grafana/public/build/zipkin*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/azuremonitor
RUN rm -rf /usr/share/grafana/public/build/azureMonitor*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/cloudwatch
RUN rm -rf /usr/share/grafana/public/build/cloudwatch*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/cloud-monitoring
RUN rm -rf /usr/share/grafana/public/build/cloudMonitoring*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/parca
RUN rm -rf /usr/share/grafana/public/build/parca*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/phlare
RUN rm -rf /usr/share/grafana/public/build/phlare*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/grafana-pyroscope-datasource
RUN rm -rf /usr/share/grafana/public/build/pyroscope*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/alertmanager
RUN rm -rf /usr/share/grafana/public/build/alertmanager*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/loki
RUN rm -rf /usr/share/grafana/public/build/loki*
RUN rm -rf /usr/share/grafana/public/app/plugins/datasource/prometheus
RUN rm -rf /usr/share/grafana/public/build/prometheus*

RUN find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|.id==="enterprise"|.id==="notanenterprise"|g' {} \;
RUN find /usr/share/grafana/public/build/ -name *.js -exec sed -i 's|.id==="cloud"|.id==="notacloud"|g' {} \;

##################################################################
## CLEANING Remove Native Panels
##################################################################
RUN rm -rf /usr/share/grafana/public/app/plugins/panel/alertlist
RUN rm -rf /usr/share/grafana/public/app/plugins/panel/annolist
RUN rm -rf /usr/share/grafana/public/app/plugins/panel/dashlist
RUN rm -rf /usr/share/grafana/public/app/plugins/panel/news
RUN rm -rf /usr/share/grafana/public/app/plugins/panel/table-old
RUN rm -rf /usr/share/grafana/public/app/plugins/panel/traces
RUN rm -rf /usr/share/grafana/public/app/plugins/panel/flamegraph

##################################################################
## INCLUDE INITIALIZATION Python script via API after boot
##################################################################
COPY --chown=grafana:0 --chmod=755 grafana-customization/run_aqdr_ui.sh /aqdr-ui/run_aqdr_ui.sh
RUN mkdir -p /aqdr-ui/grafana-initialization
COPY --chown=grafana:0 --chmod=755 grafana-initialization/ /aqdr-ui/grafana-initialization
WORKDIR /aqdr-ui/grafana-initialization
RUN apk add --update python3~3.12 poetry ca-certificates && ln -sf python3 /usr/bin/python
# --no-cache --allow-untrusted -v --repository=https://dl-cdn.alpinelinux.org/alpine/v3.20/main
RUN mkdir -p /usr/share/grafana/.local/bin
#RUN chmod 755 /usr/share/grafana/.local/bin
#RUN chown grafana:root /usr/share/grafana/.local/bin
RUN mkdir -p /usr/share/grafana/.config
#RUN chmod 755 /usr/share/grafana/.config
#RUN chown grafana:root /usr/share/grafana/.config

##################################################################
RUN chown grafana:0 /aqdr-ui/run_aqdr_ui.sh
RUN chmod 777 /aqdr-ui/run_aqdr_ui.sh
RUN chmod u+s /bin/su
#RUN usermod -s /bin/bash grafana
EXPOSE 3000
ENTRYPOINT [ "/bin/bash", "/aqdr-ui/run_aqdr_ui.sh" ]
