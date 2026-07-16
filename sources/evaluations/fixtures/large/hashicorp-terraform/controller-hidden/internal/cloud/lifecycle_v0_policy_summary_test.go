// Copyright IBM Corp. 2014, 2026
// SPDX-License-Identifier: BUSL-1.1
package cloud

import (
    "context"
    "strings"
    "testing"

    tfe "github.com/hashicorp/go-tfe"
    "github.com/mitchellh/colorstring"

    "github.com/hashicorp/terraform/internal/command/jsonformat"
    "github.com/hashicorp/terraform/internal/terminal"
)

type lifecycleFakeTFPolicyOutcomes struct {
    pages [][]*tfe.TFPolicySetOutcome
    calls []int
}

func (f *lifecycleFakeTFPolicyOutcomes) List(_ context.Context, _ string, opts *tfe.TFPolicyEvaluationListOptions) (*tfe.TFPolicyEvaluationOutcomeList, error) {
    page := 1
    if opts != nil && opts.PageNumber > 0 {
        page = opts.PageNumber
    }
    f.calls = append(f.calls, page)

    total := len(f.pages)
    next := 0
    if page < total {
        next = page + 1
    }
    return &tfe.TFPolicyEvaluationOutcomeList{
        Pagination: &tfe.Pagination{CurrentPage: page, NextPage: next, TotalPages: total},
        Items:      f.pages[page-1],
    }, nil
}

func TestCloud_renderTFPolicyEvaluations_pagination(t *testing.T) {
    b, mocks, cleanup := testBackendAndMocksWithName(t)
    t.Cleanup(cleanup)

    stream, done := terminal.StreamsForTesting(t)
    b.renderer = &jsonformat.Renderer{
        Streams:  stream,
        Colorize: &colorstring.Colorize{Disable: true},
    }

    evaluation := &tfe.TFPolicyEvaluation{
        ID:        "tfpe-123",
        StageType: tfe.TFPolicyEvaluationStageTypePlan,
        Status:    tfe.TFPolicyEvaluationStatusPassed,
    }
    run := &tfe.Run{
        ID:                  "run-123",
        Plan:                &tfe.Plan{},
        TFPolicyEvaluations: []*tfe.TFPolicyEvaluation{evaluation},
    }
    mocks.Runs.Runs[run.ID] = run

    fake := &lifecycleFakeTFPolicyOutcomes{
        pages: [][]*tfe.TFPolicySetOutcome{
            {{PolicySetName: "set-a", Outcomes: []*tfe.TFPolicySetPolicyOutcome{{PolicyName: "policy-a", Status: "passed"}}}},
            {{PolicySetName: "set-b", Outcomes: []*tfe.TFPolicySetPolicyOutcome{{PolicyName: "policy-b", Status: "passed"}}}},
        },
    }
    b.client.TFPolicyEvaluationOutcomes = fake

    if err := lifecycleRenderTFPolicyEvaluations(b, context.Background(), run, tfe.TFPolicyEvaluationStageTypePlan); err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    got := done(t).Stdout()

    if len(fake.calls) != 2 || fake.calls[0] != 1 || fake.calls[1] != 2 {
        t.Errorf("want page requests [1 2], got %v", fake.calls)
    }
    for _, want := range []string{"set-a", "set-b", "policy-a", "policy-b", "2 policies evaluated"} {
        if !strings.Contains(got, want) {
            t.Errorf("paginated render missing %q\n--- got ---\n%s", want, got)
        }
    }
}

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
