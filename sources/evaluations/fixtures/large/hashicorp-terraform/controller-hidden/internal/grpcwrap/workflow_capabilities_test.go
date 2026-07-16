// Copyright IBM Corp. 2014, 2026
// SPDX-License-Identifier: BUSL-1.1

package grpcwrap

import (
	"context"
	"reflect"
	"testing"

	"github.com/zclconf/go-cty/cty"
	"github.com/zclconf/go-cty/cty/msgpack"

	"github.com/hashicorp/terraform/internal/configs/configschema"
	"github.com/hashicorp/terraform/internal/providers"
	providerstest "github.com/hashicorp/terraform/internal/providers/testing"
	"github.com/hashicorp/terraform/internal/tfplugin5"
	"github.com/hashicorp/terraform/internal/tfplugin6"
)

func reviewActionProvider() *providerstest.MockProvider {
	p := &providerstest.MockProvider{}
	p.GetProviderSchemaResponse = &providers.GetProviderSchemaResponse{
		Provider: providers.Schema{Body: &configschema.Block{}},
		Actions: map[string]providers.ActionSchema{
			"test": {ConfigSchema: &configschema.Block{}},
		},
	}
	return p
}

func reviewEmptyDynamicValue5(t *testing.T) *tfplugin5.DynamicValue {
	t.Helper()
	raw, err := msgpack.Marshal(cty.EmptyObjectVal, cty.EmptyObject)
	if err != nil {
		t.Fatal(err)
	}
	return &tfplugin5.DynamicValue{Msgpack: raw}
}

func reviewEmptyDynamicValue6(t *testing.T) *tfplugin6.DynamicValue {
	t.Helper()
	raw, err := msgpack.Marshal(cty.EmptyObjectVal, cty.EmptyObject)
	if err != nil {
		t.Fatal(err)
	}
	return &tfplugin6.DynamicValue{Msgpack: raw}
}

func reviewComputedBlocksAllowed(capabilities providers.ClientCapabilities) bool {
	field := reflect.ValueOf(capabilities).FieldByName("ComputedBlocksAllowed")
	return field.IsValid() && field.Kind() == reflect.Bool && field.Bool()
}

func TestWorkflowComputedBlocksCapabilityAcrossGRPCWrappers(t *testing.T) {
	t.Run("protocol5", func(t *testing.T) {
		p := reviewActionProvider()
		server := Provider(p)
		_, err := server.PlanAction(context.Background(), &tfplugin5.PlanAction_Request{
			ActionType: "test",
			Config:     reviewEmptyDynamicValue5(t),
		})
		if err != nil {
			t.Fatal(err)
		}
		if !reviewComputedBlocksAllowed(p.PlanActionRequest.ClientCapabilities) {
			t.Fatal("protocol 5 wrapper dropped the computed-block capability")
		}
	})

	t.Run("protocol6", func(t *testing.T) {
		p := reviewActionProvider()
		server := Provider6(p)
		_, err := server.PlanAction(context.Background(), &tfplugin6.PlanAction_Request{
			ActionType: "test",
			Config:     reviewEmptyDynamicValue6(t),
		})
		if err != nil {
			t.Fatal(err)
		}
		if !reviewComputedBlocksAllowed(p.PlanActionRequest.ClientCapabilities) {
			t.Fatal("protocol 6 wrapper dropped the computed-block capability")
		}
	})
}
