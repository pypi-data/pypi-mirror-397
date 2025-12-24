//! SQLite persistence layer for Atlas.
//!
//! Stores artifacts and file metadata in an embedded SQLite database.

mod migrations;
mod repository;
mod schema;

pub use migrations::run_migrations;
pub use repository::AtlasRepository;
pub use schema::Schema;
