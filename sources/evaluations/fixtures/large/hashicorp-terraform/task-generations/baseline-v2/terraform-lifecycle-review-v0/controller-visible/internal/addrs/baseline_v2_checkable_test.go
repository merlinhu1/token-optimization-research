// Copyright IBM Corp. 2014, 2026
// SPDX-License-Identifier: BUSL-1.1

package addrs

import "testing"

func TestBaselineV2ParseInputVariableCheckable(t *testing.T) {
	got, diags := ParseCheckableStr(CheckableInputVariable, "var.example")
	if diags.HasErrors() {
		t.Fatalf("unexpected diagnostics: %s", diags.Err())
	}
	if got.String() != "var.example" {
		t.Fatalf("wrong address: %s", got.String())
	}
}
