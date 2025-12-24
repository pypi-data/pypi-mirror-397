//! Real-project evaluation harness for Atlas span-first search.
//!
//! This test is **gated by environment variables** so that it does not run in
//! CI by default. When enabled, it:
//! - Loads a real project path from `RANEX_EVAL_PROJECT_ROOT`
//! - Loads a label JSON file from `RANEX_EVAL_LABELS_PATH`
//! - Runs `Atlas::scan()` + `Atlas::search_spans()`
//! - Computes precision, recall, and Fβ (β = 0.5) for each query and
//!   macro-averaged Fβ across all queries.
//!
//! JSON format for labels:
//!
//! ```json
//! [
//!   {
//!     "query": "calculate_tax",
//!     "labels": [
//!       { "file_path": "app/utils.py", "line_start": 10, "line_end": 20 }
//!     ]
//!   }
//! ]
//! ```

use ranex_atlas::{Atlas, SpanResult};
use serde::Deserialize;
use std::error::Error;
use std::path::PathBuf;

#[derive(Debug, Clone, Deserialize)]
struct JsonLabelSpan {
    file_path: String,
    line_start: usize,
    line_end: usize,
}

#[derive(Debug, Clone, Deserialize)]
struct JsonEvalCase {
    query: String,
    labels: Vec<JsonLabelSpan>,
}

#[derive(Debug, Clone)]
struct LabelSpan {
    file_path: String,
    line_start: usize,
    line_end: usize,
}

#[derive(Debug, Clone)]
struct EvalCase {
    query: String,
    labels: Vec<LabelSpan>,
}

#[derive(Debug, Clone)]
struct Metrics {
    tp: usize,
    fp: usize,
    fn_: usize,
    precision: f64,
    recall: f64,
    f_beta: f64,
}

fn f_beta(precision: f64, recall: f64, beta: f64) -> f64 {
    if precision == 0.0 && recall == 0.0 {
        return 0.0;
    }
    let b2 = beta * beta;
    (1.0 + b2) * precision * recall / (b2 * precision + recall)
}

fn span_overlaps(pred: &SpanResult, label: &LabelSpan) -> bool {
    let same_file = pred.file_path.to_string_lossy() == label.file_path;
    if !same_file {
        return false;
    }

    let p_start = pred.line_start;
    let p_end = pred.line_end;
    let l_start = label.line_start;
    let l_end = label.line_end;

    // Simple range overlap check
    p_start <= l_end && l_start <= p_end
}

fn evaluate_case(spans: &[SpanResult], case: &EvalCase, beta: f64) -> Metrics {
    let mut tp = 0usize;
    let mut fp = 0usize;

    for span in spans {
        if case.labels.iter().any(|label| span_overlaps(span, label)) {
            tp += 1;
        } else {
            fp += 1;
        }
    }

    let mut fn_ = 0usize;
    for label in &case.labels {
        if !spans.iter().any(|span| span_overlaps(span, label)) {
            fn_ += 1;
        }
    }

    let precision = if tp + fp == 0 {
        0.0
    } else {
        tp as f64 / (tp + fp) as f64
    };

    let recall = if tp + fn_ == 0 {
        0.0
    } else {
        tp as f64 / (tp + fn_) as f64
    };

    let f = f_beta(precision, recall, beta);

    Metrics {
        tp,
        fp,
        fn_,
        precision,
        recall,
        f_beta: f,
    }
}

#[test]
fn eval_search_spans_real_project() -> Result<(), Box<dyn Error>> {
    // Gated by env vars to avoid running in CI by default.
    let project_root = match std::env::var("RANEX_EVAL_PROJECT_ROOT") {
        Ok(path) => PathBuf::from(path),
        Err(_) => {
            eprintln!(
                "[real_search_eval_tests] Skipping: RANEX_EVAL_PROJECT_ROOT not set"
            );
            return Ok(());
        }
    };

    let labels_path = match std::env::var("RANEX_EVAL_LABELS_PATH") {
        Ok(path) => PathBuf::from(path),
        Err(_) => {
            eprintln!(
                "[real_search_eval_tests] Skipping: RANEX_EVAL_LABELS_PATH not set"
            );
            return Ok(());
        }
    };

    let bytes = std::fs::read(&labels_path)?;
    let json_cases: Vec<JsonEvalCase> = serde_json::from_slice(&bytes)?;

    let cases: Vec<EvalCase> = json_cases
        .into_iter()
        .map(|c| EvalCase {
            query: c.query,
            labels: c
                .labels
                .into_iter()
                .map(|l| LabelSpan {
                    file_path: l.file_path,
                    line_start: l.line_start,
                    line_end: l.line_end,
                })
                .collect(),
        })
        .collect();

    if cases.is_empty() {
        eprintln!(
            "[real_search_eval_tests] No cases loaded from {:?}, nothing to evaluate",
            labels_path
        );
        return Ok(());
    }

    let mut atlas = Atlas::new(&project_root)?;
    atlas.scan()?;

    let beta = 0.5;
    let mut all_metrics = Vec::new();

    for case in &cases {
        let spans = atlas.search_spans(&case.query, 50)?;
        let metrics = evaluate_case(&spans, case, beta);

        println!(
            "[real_search_eval] query={:?} tp={} fp={} fn={} precision={:.3} recall={:.3} F_{:.1}={:.3}",
            case.query,
            metrics.tp,
            metrics.fp,
            metrics.fn_,
            metrics.precision,
            metrics.recall,
            beta,
            metrics.f_beta
        );

        all_metrics.push(metrics);
    }

    let avg_f_beta: f64 = all_metrics
        .iter()
        .map(|m| m.f_beta)
        .sum::<f64>()
        / all_metrics.len() as f64;

    println!(
        "[real_search_eval] cases={} avg_F_{:.1}={:.3}",
        all_metrics.len(),
        beta,
        avg_f_beta
    );

    // Optional enforcement: if RANEX_EVAL_MIN_FBETA is set, treat it as a
    // minimum acceptable macro-averaged F_{0.5} and fail the test if we drop
    // below it. This keeps CI unaffected by default but allows local gating.
    if let Ok(min_s) = std::env::var("RANEX_EVAL_MIN_FBETA")
        && let Ok(min) = min_s.parse::<f64>()
    {
        assert!(
            avg_f_beta >= min,
            "Macro-averaged F_{{0.5}} ({:.3}) is below configured minimum ({:.3})",
            avg_f_beta,
            min
        );
    }

    Ok(())
}
