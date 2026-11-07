# Conftest policy for Argo CD / Argo Rollouts manifests in a GitOps repo.
# Status: written, NOT executed locally (opa/conftest not installed in the factory). TODO-VERIFY with `conftest test --policy policies/opa-conftest <manifests>`.
package argocd_gitops

import rego.v1

# Applications must not live in the permissive `default` AppProject.
deny contains msg if {
	input.kind == "Application"
	object.get(input.spec, "project", "default") == "default"
	msg := sprintf("Application %s uses AppProject 'default' (permits any repo/cluster/kind); use a restricted AppProject", [input.metadata.name])
}

# AppProjects must not allow any source repository.
deny contains msg if {
	input.kind == "AppProject"
	some repo in input.spec.sourceRepos
	repo == "*"
	msg := sprintf("AppProject %s allows sourceRepos '*'", [input.metadata.name])
}

# AppProjects must not allow any destination server or namespace.
deny contains msg if {
	input.kind == "AppProject"
	some dest in input.spec.destinations
	dest.namespace == "*"
	msg := sprintf("AppProject %s has a destination with namespace '*'", [input.metadata.name])
}

deny contains msg if {
	input.kind == "AppProject"
	some dest in input.spec.destinations
	dest.server == "*"
	msg := sprintf("AppProject %s has a destination with server '*'", [input.metadata.name])
}

# Canary Rollouts must have analysis (inline step or background).
deny contains msg if {
	input.kind == "Rollout"
	input.spec.strategy.canary
	not has_analysis(input.spec.strategy.canary)
	msg := sprintf("Rollout %s uses canary without any analysis (step or background)", [input.metadata.name])
}

has_analysis(canary) if canary.analysis

has_analysis(canary) if {
	some step in canary.steps
	step.analysis
}
