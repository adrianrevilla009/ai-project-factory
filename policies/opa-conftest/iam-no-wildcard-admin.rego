# Conftest policy: deny IAM policies that grant Action "*" on Resource "*"
# (skill: iam-governance-and-pam). Static check on a Terraform plan JSON only.
# Usage: conftest test tfplan.json -p policies/opa-conftest
package main

import rego.v1

statements(doc) := s if {
	is_array(doc.Statement)
	s := doc.Statement
}

statements(doc) := [doc.Statement] if {
	is_object(doc.Statement)
}

as_list(x) := x if is_array(x)

as_list(x) := [x] if is_string(x)

deny contains msg if {
	some r in input.planned_values.root_module.resources
	r.type == "aws_iam_policy"
	doc := json.unmarshal(r.values.policy)
	some st in statements(doc)
	st.Effect == "Allow"
	"*" in as_list(st.Action)
	"*" in as_list(st.Resource)
	msg := sprintf("aws_iam_policy.%s allows Action * on Resource * (admin wildcard); use scoped actions or a documented break-glass role", [r.name])
}
