# Conftest: reglas de seguridad de malla Istio (skills mtls-strict-and-peer-auth, authorization-policies).
# Uso: conftest test --policy policies/opa-conftest <manifiestos.yaml>
package main

import rego.v1

deny contains msg if {
	input.kind == "PeerAuthentication"
	mode := input.spec.mtls.mode
	mode in {"PERMISSIVE", "DISABLE"}
	msg := sprintf("PeerAuthentication %s usa mtls.mode=%s; usar STRICT (excepcion documentada en ADR)", [input.metadata.name, mode])
}

deny contains msg if {
	input.kind == "AuthorizationPolicy"
	some rule in input.spec.rules
	some from in rule.from
	"*" in from.source.principals
	msg := sprintf("AuthorizationPolicy %s permite principals '*'; listar identidades concretas", [input.metadata.name])
}
