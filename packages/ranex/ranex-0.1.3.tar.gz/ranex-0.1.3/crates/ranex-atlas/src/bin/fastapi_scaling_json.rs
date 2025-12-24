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
            eprintln!("Usage: fastapi_scaling_json <project_root>");
            std::process::exit(1);
        }
    };

    let project_root = Path::new(project_root_arg);

    let mut atlas = Atlas::new(project_root)?;
    let report = atlas.analyze_fastapi_scaling()?;

    let json = serde_json::to_string_pretty(&report)?;
    println!("{}", json);

    Ok(())
}
