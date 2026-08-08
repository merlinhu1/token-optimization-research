// Copyright IBM Corp. 2014, 2026
// SPDX-License-Identifier: BUSL-1.1

package callback

import (
	"context"
	"testing"

	"github.com/hashicorp/terraform/internal/policy/proto"
	"github.com/zclconf/go-cty/cty"
	"github.com/zclconf/go-cty/cty/msgpack"
)

func TestBaselineV3DeferredDataSource(t *testing.T) {
	registry := NewRegistry()
	registry.Register(1, Functions{GetDataSource: func(context.Context, string, cty.Value) (cty.Value, bool, error) {
		return cty.StringVal("ready"), true, nil
	}})
	config, err := msgpack.Marshal(cty.StringVal("config"), cty.DynamicPseudoType)
	if err != nil {
		t.Fatal(err)
	}
	response, err := (&Server{Registry: registry}).GetDataSource(context.Background(), &proto.GetDataSourceRequest{Type: "example", Config: config, EvaluationRequestId: 1})
	if err != nil {
		t.Fatal(err)
	}
	if !response.Deferred {
		t.Fatal("expected deferred response")
	}
}
