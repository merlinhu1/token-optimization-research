// Copyright IBM Corp. 2014, 2026
// SPDX-License-Identifier: BUSL-1.1

package configs

import (
	"reflect"
	"strings"
	"testing"
)

func TestBaselineV2StateStoreRequirementNamedType(t *testing.T) {
	field, ok := reflect.TypeOf(StateStoreProviderRequirement{}).FieldByName("Requirement")
	if !ok {
		t.Fatal("Requirement field is missing")
	}
	if field.Type.Name() != "Requirements" || !strings.HasSuffix(field.Type.PkgPath(), "/providerreqs") {
		t.Fatalf("Requirement must use providerreqs.Requirements, got %s", field.Type)
	}
}
