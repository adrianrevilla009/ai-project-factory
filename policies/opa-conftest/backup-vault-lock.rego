# Conftest policy: every aws_backup_vault must have a lock configuration with
# a minimum retention (skill: backup-vault-immutability-and-restore-tests).
# Usage (static only, nothing is deployed): conftest test tfplan.json -p policies/opa-conftest
package main

import rego.v1

vaults contains name if {
	some r in input.planned_values.root_module.resources
	r.type == "aws_backup_vault"
	name := r.name
}

locked contains name if {
	some r in input.planned_values.root_module.resources
	r.type == "aws_backup_vault_lock_configuration"
	r.values.min_retention_days >= 1
	name := r.name
}

deny contains msg if {
	some v in vaults
	not locked[v]
	msg := sprintf("aws_backup_vault.%s has no aws_backup_vault_lock_configuration with min_retention_days (pending: match by vault name instead of resource name)", [v])
}
