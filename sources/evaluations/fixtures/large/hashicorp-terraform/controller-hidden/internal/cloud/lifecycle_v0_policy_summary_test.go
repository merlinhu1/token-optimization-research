// Copyright IBM Corp. 2014, 2026
// SPDX-License-Identifier: BUSL-1.1
package cloud

import (
    "strings"
    "testing"

    tfe "github.com/hashicorp/go-tfe"
    "github.com/hashicorp/terraform/internal/command/jsonformat"
    "github.com/hashicorp/terraform/internal/terminal"
)

func TestLifecycleV0PolicySummaryCountsRenderedOutcomes(t *testing.T) {
    b, cleanup := testBackendWithName(t)
    t.Cleanup(cleanup)
    stream, done := terminal.StreamsForTesting(t)
    b.renderer = &jsonformat.Renderer{Streams: stream, Colorize: mockColorize()}
    b.writeTFPolicyEvaluations([]tfPolicyStageOutcomes{{
        eval: &tfe.TFPolicyEvaluation{
            StageType: tfe.TFPolicyEvaluationStageTypePlan,
            Status: tfe.TFPolicyEvaluationStatusPassed,
            ResultCount: &tfe.TFPolicyEvaluationResultCount{Passed: 99},
        },
        sets: []*tfe.TFPolicySetOutcome{{Outcomes: []*tfe.TFPolicySetPolicyOutcome{
            {PolicyName: "first", Status: "passed"},
            {PolicyName: "second", Status: "passed"},
        }}},
    }})
    got := done(t).Stdout()
    if !strings.Contains(got, "2 policies evaluated") {
        t.Fatalf("summary total must match rendered outcomes; got:\n%s", got)
    }
    if strings.Contains(got, "99 policies evaluated") {
        t.Fatalf("summary trusted stale aggregate instead of rendered outcomes:\n%s", got)
    }
}
