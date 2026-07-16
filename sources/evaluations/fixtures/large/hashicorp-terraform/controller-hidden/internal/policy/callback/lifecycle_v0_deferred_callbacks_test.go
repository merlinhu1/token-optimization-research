// Copyright IBM Corp. 2014, 2026
// SPDX-License-Identifier: BUSL-1.1
package callback

import (
    "context"
    "reflect"
    "testing"

    "github.com/hashicorp/terraform/internal/policy/proto"
    "github.com/zclconf/go-cty/cty"
    "github.com/zclconf/go-cty/cty/msgpack"
)

var (
    ctyValueType = reflect.TypeOf(cty.NilVal)
    ctyValuesType = reflect.TypeOf([]cty.Value{})
    errorType = reflect.TypeOf((*error)(nil)).Elem()
)

func callbackFunction(t *testing.T, typ reflect.Type, value cty.Value) reflect.Value {
    t.Helper()
    return reflect.MakeFunc(typ, func(_ []reflect.Value) []reflect.Value {
        out := make([]reflect.Value, typ.NumOut())
        for i := range out {
            ot := typ.Out(i)
            switch {
            case ot == ctyValueType:
                out[i] = reflect.ValueOf(value)
            case ot == ctyValuesType:
                out[i] = reflect.ValueOf([]cty.Value{value})
            case ot.Kind() == reflect.Bool:
                out[i] = reflect.ValueOf(true)
            case ot.Implements(errorType):
                out[i] = reflect.Zero(ot)
            default:
                t.Fatalf("unexpected callback output type %s", ot)
            }
        }
        return out
    })
}

func TestLifecycleV0DeferredCallbacksPreserveState(t *testing.T) {
    value := cty.ObjectVal(map[string]cty.Value{"id": cty.StringVal("deferred")})
    attrs, err := msgpack.Marshal(cty.EmptyObjectVal, cty.DynamicPseudoType)
    if err != nil { t.Fatal(err) }

    fns := Functions{}
    fv := reflect.ValueOf(&fns).Elem()
    for _, name := range []string{"GetResources", "GetDataSource"} {
        field := fv.FieldByName(name)
        field.Set(callbackFunction(t, field.Type(), value))
    }
    registry := NewRegistry()
    registry.Register(7, fns)
    server := &Server{ID: 7, Registry: registry}

    resources, err := server.GetResources(context.Background(), &proto.GetResourcesRequest{
        EvaluationRequestId: 7, Type: "example_resource", Attributes: attrs,
    })
    if err != nil { t.Fatal(err) }
    if !resources.Partial { t.Fatal("deferred resource matches must produce a partial response") }
    if len(resources.Results) != 1 { t.Fatalf("got %d resource results; want 1", len(resources.Results)) }

    datasource, err := server.GetDataSource(context.Background(), &proto.GetDataSourceRequest{
        EvaluationRequestId: 7, Type: "example_data_source", Config: attrs,
    })
    if err != nil { t.Fatal(err) }
    if !datasource.Deferred { t.Fatal("data-source callback must preserve the deferred state") }
}
