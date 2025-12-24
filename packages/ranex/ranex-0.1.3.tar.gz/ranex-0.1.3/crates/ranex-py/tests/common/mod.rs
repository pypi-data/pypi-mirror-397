//! Shared test utilities for ranex-py integration tests.

use std::path::PathBuf;
use tempfile::TempDir;

/// Create a temporary Python project for testing.
pub fn create_python_project() -> std::io::Result<TempDir> {
    let temp = TempDir::new()?;

    // Create basic project structure
    let app_dir = temp.path().join("app");
    std::fs::create_dir_all(&app_dir)?;

    // Create .ranex directory
    let ranex_dir = temp.path().join(".ranex");
    std::fs::create_dir_all(&ranex_dir)?;

    Ok(temp)
}

/// Create a Python file with given content.
pub fn create_python_file(
    project: &TempDir,
    relative_path: &str,
    content: &str,
) -> std::io::Result<PathBuf> {
    let file_path = project.path().join(relative_path);

    // Create parent directories
    if let Some(parent) = file_path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    std::fs::write(&file_path, content)?;
    Ok(file_path)
}

/// Create a sample Python project with various artifacts.
pub fn create_sample_project() -> std::io::Result<TempDir> {
    let project = create_python_project()?;

    // Main module with function
    create_python_file(
        &project,
        "app/main.py",
        r#"
"""Main application module."""

def main():
    """Application entry point."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
"#,
    )?;

    // Utility module with multiple functions
    create_python_file(
        &project,
        "app/utils.py",
        r#"
"""Utility functions."""

MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

def calculate_tax(amount: float, rate: float = 0.1) -> float:
    """Calculate tax on the given amount.
    
    Args:
        amount: The base amount.
        rate: Tax rate (default 10%).
    
    Returns:
        The calculated tax.
    """
    return amount * rate

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    return f"{currency} {amount:.2f}"

class Helper:
    """A helper class."""
    
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello, {self.name}!"
"#,
    )?;

    // Feature module
    create_python_file(
        &project,
        "app/features/payment/service.py",
        r#"
"""Payment service module."""

from typing import Optional

class PaymentService:
    """Handles payment processing."""
    
    def process_payment(self, amount: float, currency: str = "USD") -> bool:
        """Process a payment.
        
        Args:
            amount: Payment amount.
            currency: Currency code.
        
        Returns:
            True if successful.
        """
        return amount > 0

async def async_refund(payment_id: str) -> dict:
    """Process a refund asynchronously."""
    return {"status": "refunded", "id": payment_id}
"#,
    )?;

    Ok(project)
}

/// Create an empty project (no Python files).
pub fn create_empty_project() -> std::io::Result<TempDir> {
    create_python_project()
}
