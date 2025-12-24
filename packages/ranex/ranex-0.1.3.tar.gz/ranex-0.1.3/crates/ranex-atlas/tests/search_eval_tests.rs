//! Evaluation harness for Atlas span-first search.
//!
//! This integration test builds a small labeled dataset of
//! (query, ground-truth spans) and computes precision, recall,
//! and Fβ (β = 0.5) for `Atlas::search_spans`.
//!
//! The goal is to provide a reproducible way to tune the
//! ranking constants in `search_spans` rather than relying
//! purely on hand-picked weights.

use ranex_atlas::Atlas;
use ranex_atlas::SpanResult;
use std::error::Error;

mod common;

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
fn eval_search_spans_small_dataset() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    // Exercise shared helpers in this binary to avoid dead-code warnings.
    let _ = common::create_sample_project()?;
    let _ = common::create_project_with_error()?;

    // Construct a small, labeled project so line numbers are stable.
    //
    // File: app/utils.py
    //  1: """Utils module"""
    //  2:
    //  3: def calculate_tax(amount: float, rate: float = 0.1) -> float:
    //  4:     return amount * rate
    //  5:
    //  6: def process_payment(amount: float) -> float:
    //  7:     tax = calculate_tax(amount)
    //  8:     return amount + tax
    let code = r#"""Utils module"""


def calculate_tax(amount: float, rate: float = 0.1) -> float:
    return amount * rate


def process_payment(amount: float) -> float:
    tax = calculate_tax(amount)
    return amount + tax
"#;

    common::create_python_file(&project, "app/utils.py", code)?;

    // File: app/models.py
    //  1: from pydantic import BaseModel
    //  2:
    //  3: class ItemIn(BaseModel):
    //  4:     name: str
    //  5:
    //  6: class ItemOut(BaseModel):
    //  7:     id: int
    //  8:     name: str
    let models_code = r#"from pydantic import BaseModel


class ItemIn(BaseModel):
    name: str


class ItemOut(BaseModel):
    id: int
    name: str
"#;

    common::create_python_file(&project, "app/models.py", models_code)?;

    // File: app/api.py
    //  1: from fastapi import APIRouter
    //  2: from .models import ItemIn, ItemOut
    //  3:
    //  4: router = APIRouter()
    //  5:
    //  6: @router.post("/items", response_model=ItemOut)
    //  7: async def create_item(item: ItemIn) -> ItemOut:
    //  8:     return ItemOut(id=1, name=item.name)
    let api_code = r#"from fastapi import APIRouter
from .models import ItemIn, ItemOut


router = APIRouter()


@router.post("/items", response_model=ItemOut)
async def create_item(item: ItemIn) -> ItemOut:
    return ItemOut(id=1, name=item.name)
"#;

    common::create_python_file(&project, "app/api.py", api_code)?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let cases = vec![
        EvalCase {
            query: "calculate_tax".to_string(),
            labels: vec![LabelSpan {
                file_path: "app/utils.py".to_string(),
                line_start: 3,
                line_end: 4,
            }],
        },
        EvalCase {
            query: "process_payment".to_string(),
            labels: vec![LabelSpan {
                file_path: "app/utils.py".to_string(),
                line_start: 6,
                line_end: 8,
            }],
        },
        // Endpoint query: function name
        EvalCase {
            query: "create_item".to_string(),
            labels: vec![LabelSpan {
                file_path: "app/api.py".to_string(),
                line_start: 7,
                line_end: 8,
            }],
        },
        // Endpoint query: route path segment
        EvalCase {
            query: "/items".to_string(),
            labels: vec![LabelSpan {
                file_path: "app/api.py".to_string(),
                line_start: 6,
                line_end: 8,
            }],
        },
        // Model query: Pydantic model name
        EvalCase {
            query: "ItemOut".to_string(),
            labels: vec![LabelSpan {
                file_path: "app/models.py".to_string(),
                line_start: 6,
                line_end: 8,
            }],
        },
        // Cross-file query: generic type name that appears in models and API.
        // For this case we treat both model definitions and the API usage as
        // relevant spans.
        EvalCase {
            query: "Item".to_string(),
            labels: vec![
                LabelSpan {
                    file_path: "app/models.py".to_string(),
                    line_start: 3,
                    line_end: 4,
                },
                LabelSpan {
                    file_path: "app/models.py".to_string(),
                    line_start: 6,
                    line_end: 8,
                },
                LabelSpan {
                    file_path: "app/api.py".to_string(),
                    line_start: 2,
                    line_end: 2,
                },
            ],
        },
    ];

    let beta = 0.5;
    let mut all_metrics = Vec::new();

    for case in &cases {
        let spans = atlas.search_spans(&case.query, 10)?;
        let metrics = evaluate_case(&spans, case, beta);

        // Emit metrics to stdout so humans can compare different weight settings
        // when tuning search_spans.
        println!(
            "query={:?} tp={} fp={} fn={} precision={:.3} recall={:.3} F_{:.1}={:.3}",
            case.query, metrics.tp, metrics.fp, metrics.fn_, metrics.precision, metrics.recall, beta, metrics.f_beta
        );

        all_metrics.push(metrics);
    }

    // Aggregate simple macro-averaged F_beta over cases.
    let avg_f_beta: f64 = if all_metrics.is_empty() {
        0.0
    } else {
        all_metrics.iter().map(|m| m.f_beta).sum::<f64>() / all_metrics.len() as f64
    };

    // For this controlled dataset we expect reasonably high precision and recall.
    // If F_{0.5} drops below 0.55, it is a signal that the ranking weights in
    // `search_spans` may need to be revisited.
    assert!(
        avg_f_beta >= 0.55,
        "Average F_{{0.5}} too low for small dataset: {:.3}",
        avg_f_beta
    );

    Ok(())
}
