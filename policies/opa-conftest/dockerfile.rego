# Conftest policy for Dockerfiles: `conftest test --parser dockerfile -p policies/opa-conftest Dockerfile`
# Rego v1 syntax requires a recent OPA/Conftest; check the version pinned by the project.
package dockerfile

import rego.v1

stage_names contains lower(input[i].Value[2]) if {
	input[i].Cmd == "from"
	count(input[i].Value) == 3
}

last_segment(image) := s if {
	parts := split(image, "/")
	s := parts[count(parts) - 1]
}

deny contains msg if {
	some i
	input[i].Cmd == "from"
	image := input[i].Value[0]
	image != "scratch"
	not lower(image) in stage_names
	not contains(image, "@sha256:")
	not contains(last_segment(image), ":")
	msg := sprintf("FROM %s has no tag or digest; pin a version or digest", [image])
}

deny contains msg if {
	some i
	input[i].Cmd == "from"
	image := input[i].Value[0]
	endswith(lower(image), ":latest")
	msg := sprintf("FROM %s uses the mutable tag latest", [image])
}

users := [u | some i; input[i].Cmd == "user"; u := input[i].Value[0]]

deny contains "Dockerfile must set a non-root USER" if {
	count(users) == 0
}

deny contains "final USER must not be root" if {
	count(users) > 0
	users[count(users) - 1] in {"root", "0"}
}
