/// A simple key-value store with intentional compilation errors.
/// Task: Fix all compilation errors to make the tests pass.

use std::collections::HashMap;

pub struct Store {
    data: HashMap<String, String>,
}

impl Store {
    pub fn new() -> Store {
        Store {
            data: HashMap::new(),
        }
    }

    // ERROR 1: Missing lifetime annotation
    pub fn get(&self, key: &str) -> Option<&str> {
        self.data.get(key).map(|s| s.as_str())
    }

    // ERROR 2: Wrong parameter type (should be Into<String>)
    pub fn set(&mut self, key: String, value: String) {
        self.data.insert(key, value);
    }

    // ERROR 3: Missing mutable reference
    pub fn delete(&self, key: &str) -> Option<String> {
        self.data.remove(key)  // This won't compile - need &mut self
    }

    // ERROR 4: Returns wrong type
    pub fn len(&self) -> i32 {
        self.data.len()  // HashMap::len returns usize, not i32
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }
}

// ERROR 5: Missing Default trait implementation
// impl Default for Store { ... }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_store_is_empty() {
        let store = Store::new();
        assert!(store.is_empty());
        assert_eq!(store.len(), 0);
    }

    #[test]
    fn test_set_and_get() {
        let mut store = Store::new();
        store.set("key1".to_string(), "value1".to_string());
        assert_eq!(store.get("key1"), Some("value1"));
    }

    #[test]
    fn test_delete() {
        let mut store = Store::new();
        store.set("key1".to_string(), "value1".to_string());
        let deleted = store.delete("key1");
        assert_eq!(deleted, Some("value1".to_string()));
        assert!(store.get("key1").is_none());
    }

    #[test]
    fn test_default() {
        let store = Store::default();
        assert!(store.is_empty());
    }
}
