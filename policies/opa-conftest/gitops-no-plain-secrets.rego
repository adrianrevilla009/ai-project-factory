# Conftest policy: no plain Kubernetes Secret with data in a GitOps repo.
# Status: written, NOT executed locally (opa/conftest not installed). TODO-VERIFY.
package gitops_no_plain_secrets

import rego.v1

deny contains msg if {
	input.kind == "Secret"
	count(object.get(input, "data", {})) + count(object.get(input, "stringData", {})) > 0
	msg := sprintf("Secret %s carries inline data in Git; use ExternalSecret/SealedSecret/Vault operator instead", [input.metadata.name])
}
