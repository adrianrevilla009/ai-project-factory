# Conftest: every `uses:` of a third-party action must be pinned by a 40-hex commit SHA (D20).
# Estado: escrita, NO ejecutada. TODO-VERIFY: probar con `conftest test --parser yaml .github/workflows/`
# y confirmar la sintaxis Rego de la version de conftest en uso.
package main

import rego.v1

is_sha(ref) if regex.match(`^[0-9a-f]{40}$`, ref)

deny contains msg if {
	some job_name, job in input.jobs
	some step in job.steps
	uses := step.uses
	not startswith(uses, "./")
	not startswith(uses, "docker://")
	parts := split(uses, "@")
	not is_sha(parts[count(parts) - 1])
	msg := sprintf("job %s: '%s' no esta fijada por SHA de commit (D20, skill github-actions)", [job_name, uses])
}

deny contains msg if {
	some job_name, job in input.jobs
	uses := job.uses
	not startswith(uses, "./")
	parts := split(uses, "@")
	not is_sha(parts[count(parts) - 1])
	msg := sprintf("job %s: workflow reutilizable '%s' sin SHA (D20)", [job_name, uses])
}

deny contains msg if {
	not input.permissions
	msg := "workflow sin bloque 'permissions:' de nivel superior (minimo privilegio)"
}
