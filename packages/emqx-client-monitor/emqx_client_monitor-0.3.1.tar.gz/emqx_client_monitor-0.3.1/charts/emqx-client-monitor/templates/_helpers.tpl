{{- define "emqx-client-monitor.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "emqx-client-monitor.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "emqx-client-monitor.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "emqx-client-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "emqx-client-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "emqx-client-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "emqx-client-monitor.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "emqx-client-monitor.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{- define "emqx-client-monitor.configSecretName" -}}
{{- if .Values.config.existingSecret -}}
{{ .Values.config.existingSecret }}
{{- else -}}
{{ printf "%s-config" (include "emqx-client-monitor.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end -}}
{{- end -}}
