use ranex_atlas::analysis::{FastapiScalingReport, ScopeKind};
use ranex_atlas::Atlas;
use std::path::Path;

fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();

    let project_root_arg = match args.as_slice() {
        [_, project_root] => project_root,
        _ => {
            eprintln!("Usage: fastapi_scaling_demo <project_root>");
            std::process::exit(1);
        }
    };

    let project_root = Path::new(project_root_arg);

    let mut atlas = Atlas::new(project_root)?;
    let report = atlas.analyze_fastapi_scaling()?;

    print_summary(&report);

    Ok(())
}

fn print_summary(report: &FastapiScalingReport) {
    println!("policy_version: {}", report.policy_version);
    println!(
        "stats: total_definitions={}, total_endpoints={}, async_endpoints={}, sync_endpoints={}, modules_with_endpoints={}",
        report.stats.total_definitions,
        report.stats.total_endpoints,
        report.stats.async_endpoints,
        report.stats.sync_endpoints,
        report.stats.modules_with_endpoints,
    );

    println!("violation_count: {}", report.violations.len());

    // Category counts
    let mut by_category: std::collections::HashMap<String, usize> =
        std::collections::HashMap::new();

    // Scope counts (explicit to avoid requiring ScopeKind: Hash)
    let mut endpoint_count = 0usize;
    let mut dependency_count = 0usize;
    let mut lifespan_count = 0usize;
    let mut middleware_count = 0usize;
    let mut background_count = 0usize;

    for v in &report.violations {
        let cat_key = v.category.clone().unwrap_or_else(|| "<none>".to_string());
        *by_category.entry(cat_key).or_insert(0) += 1;

        match v.scope {
            ScopeKind::Endpoint => endpoint_count += 1,
            ScopeKind::Dependency => dependency_count += 1,
            ScopeKind::Lifespan => lifespan_count += 1,
            ScopeKind::Middleware => middleware_count += 1,
            ScopeKind::BackgroundTask => background_count += 1,
        }
    }

    println!("categories:");
    for (cat, count) in by_category {
        println!("  {}: {}", cat, count);
    }

    println!("scopes:");
    if endpoint_count > 0 {
        println!("  Endpoint: {}", endpoint_count);
    }
    if dependency_count > 0 {
        println!("  Dependency: {}", dependency_count);
    }
    if lifespan_count > 0 {
        println!("  Lifespan: {}", lifespan_count);
    }
    if middleware_count > 0 {
        println!("  Middleware: {}", middleware_count);
    }
    if background_count > 0 {
        println!("  BackgroundTask: {}", background_count);
    }
}
