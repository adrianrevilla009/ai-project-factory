# Conftest policy: every entry of a maturity register (YAML/JSON) must use an allowed
# label, and no label may claim verification on real AWS (skill: maturity-labels,
# honest-claims-policy). Expected input shape:
#   modules:
#     - { name: network, maturity: static-validated, evidence: ["ci/run/123"] }
# Usage: conftest test docs/maturity-register.yaml -p policies/opa-conftest
package main

import rego.v1

allowed_labels := {"documented", "designed", "static-validated", "locally-exercised"}

deny contains msg if {
	some m in input.modules
	not m.maturity in allowed_labels
	msg := sprintf("module '%s': maturity '%s' is not allowed (max is static-validated; ADR-0004)", [m.name, m.maturity])
}

deny contains msg if {
	some m in input.modules
	m.maturity in {"static-validated", "locally-exercised"}
	count(object.get(m, "evidence", [])) == 0
	msg := sprintf("module '%s': maturity '%s' requires at least one evidence entry", [m.name, m.maturity])
}
