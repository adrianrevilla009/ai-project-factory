# Conftest policy: taggable AWS resources in a Terraform plan JSON must carry the
# mandatory cost-allocation tags (skill: static-verification-ladder, cost-estimation).
# Usage (static only, nothing is deployed): conftest test tfplan.json -p policies/opa-conftest
# The plan JSON must come from an offline/mocked run (ADR-0037); never from a real account.
# Limitation: only checks planned_values.root_module (child modules pending).
package main

import rego.v1

required_tags := {"project", "environment", "owner", "cost-center"}

# Resource types checked. Extend per project (pending: derive from provider schema).
taggable := {"aws_s3_bucket", "aws_dynamodb_table", "aws_db_instance", "aws_eks_cluster", "aws_msk_cluster"}

deny contains msg if {
	some r in input.planned_values.root_module.resources
	r.type in taggable
	tags := object.get(r.values, "tags", {})
	missing := required_tags - {k | some k, _ in tags}
	count(missing) > 0
	msg := sprintf("%s.%s is missing required tags: %v", [r.type, r.name, sort(missing)])
}
