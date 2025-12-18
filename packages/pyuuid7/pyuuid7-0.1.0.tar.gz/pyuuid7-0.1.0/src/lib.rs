//! PyUUID7 - Fast UUID generation in Rust for Python
//!
//! Provides UUID v4 (random), v5 (name-based), and v7 (time-sortable) generation,
//! along with validation and version identification.

use pyo3::prelude::*;
use uuid::Uuid;

/// Generate a random UUID v4.
///
/// Returns:
///     str: A new random UUID v4 string.
///
/// Example:
///     >>> import pyuuid7
///     >>> pyuuid7.uuid4()
///     'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d'
#[pyfunction]
fn uuid4() -> String {
    Uuid::new_v4().to_string()
}

/// Generate a name-based UUID v5 using SHA-1 hashing.
///
/// Args:
///     namespace: A valid UUID string representing the namespace.
///     name: The name to hash within the namespace.
///
/// Returns:
///     str: A deterministic UUID v5 string, or None if namespace is invalid.
///
/// Example:
///     >>> import pyuuid7
///     >>> pyuuid7.uuid5("6ba7b810-9dad-11d1-80b4-00c04fd430c8", "example.com")
///     '2ed6657d-e927-568b-95e1-2665a8aea6a2'
#[pyfunction]
fn uuid5(namespace: &str, name: &str) -> Option<String> {
    Uuid::parse_str(namespace)
        .ok()
        .map(|ns| Uuid::new_v5(&ns, name.as_bytes()).to_string())
}

/// Generate a time-sortable UUID v7.
///
/// UUID v7 combines a Unix timestamp with random data, making it
/// suitable for database primary keys where ordering matters.
///
/// Returns:
///     str: A new time-sortable UUID v7 string.
///
/// Example:
///     >>> import pyuuid7
///     >>> pyuuid7.uuid7()
///     '019389a1-2b3c-7d4e-8f5a-6b7c8d9e0f1a'
#[pyfunction]
fn uuid7() -> String {
    Uuid::now_v7().to_string()
}

/// Validate if a string is a valid UUID.
///
/// Args:
///     uuid_str: The string to validate.
///
/// Returns:
///     bool: True if the string is a valid UUID, False otherwise.
///
/// Example:
///     >>> import pyuuid7
///     >>> pyuuid7.is_valid("a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d")
///     True
///     >>> pyuuid7.is_valid("invalid")
///     False
#[pyfunction]
fn is_valid(uuid_str: &str) -> bool {
    Uuid::parse_str(uuid_str).is_ok()
}

/// Get the version number of a UUID.
///
/// Args:
///     uuid_str: A valid UUID string.
///
/// Returns:
///     int | None: The UUID version (1-8) or None if invalid.
///
/// Example:
///     >>> import pyuuid7
///     >>> pyuuid7.get_version("a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d")
///     4
#[pyfunction]
fn get_version(uuid_str: &str) -> Option<u8> {
    Uuid::parse_str(uuid_str)
        .ok()
        .map(|u| u.get_version_num() as u8)
}

/// Parse a UUID string and return it in canonical lowercase format.
///
/// Args:
///     uuid_str: A UUID string (can be uppercase or have different formatting).
///
/// Returns:
///     str | None: The canonical UUID string or None if invalid.
///
/// Example:
///     >>> import pyuuid7
///     >>> pyuuid7.parse("A1B2C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D")
///     'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d'
#[pyfunction]
fn parse(uuid_str: &str) -> Option<String> {
    Uuid::parse_str(uuid_str).ok().map(|u| u.to_string())
}

/// PyUUID7 Python module.
#[pymodule]
fn pyuuid7(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(uuid4, m)?)?;
    m.add_function(wrap_pyfunction!(uuid5, m)?)?;
    m.add_function(wrap_pyfunction!(uuid7, m)?)?;
    m.add_function(wrap_pyfunction!(is_valid, m)?)?;
    m.add_function(wrap_pyfunction!(get_version, m)?)?;
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_uuid4_format() {
        let id = uuid4();
        assert!(is_valid(&id));
        assert_eq!(get_version(&id), Some(4));
    }

    #[test]
    fn test_uuid5_deterministic() {
        let ns = "6ba7b810-9dad-11d1-80b4-00c04fd430c8";
        let id1 = uuid5(ns, "test");
        let id2 = uuid5(ns, "test");
        assert_eq!(id1, id2);
        assert_eq!(get_version(&id1.unwrap()), Some(5));
    }

    #[test]
    fn test_uuid7_format() {
        let id = uuid7();
        assert!(is_valid(&id));
        assert_eq!(get_version(&id), Some(7));
    }

    #[test]
    fn test_is_valid() {
        assert!(is_valid("a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"));
        assert!(!is_valid("invalid"));
        assert!(!is_valid(""));
    }

    #[test]
    fn test_parse() {
        let upper = "A1B2C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D";
        let lower = parse(upper);
        assert_eq!(
            lower,
            Some("a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d".to_string())
        );
        assert_eq!(parse("invalid"), None);
    }
}
