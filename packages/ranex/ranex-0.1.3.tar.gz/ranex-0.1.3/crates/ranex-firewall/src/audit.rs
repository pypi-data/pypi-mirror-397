//! Non-blocking ring buffer for audit events.

use crate::policy::Severity;
use parking_lot::Mutex;
use std::collections::VecDeque;

/// Audit event record
#[derive(Debug, Clone)]
pub struct AuditEvent {
    pub timestamp: u64,
    pub event_type: AuditEventType,
    pub module: String,
    pub severity: Severity,
    pub message: String,
    pub caller_file: Option<String>,
    pub caller_line: Option<u32>,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AuditEventType {
    ImportAllowed,
    ImportBlocked,
    TyposquatDetected,
    PatternBlocked,
    DynamicImport,
    CircuitOpen,
}
/// Thread-safe ring buffer for audit events
pub struct AuditRingBuffer {
    buffer: Mutex<VecDeque<AuditEvent>>,
    capacity: usize,
}

impl AuditRingBuffer {
    /// Create new ring buffer with specified capacity
    pub fn new(capacity: usize) -> Self {
        Self {
            buffer: Mutex::new(VecDeque::with_capacity(capacity)),
            capacity,
        }
    }

    /// Push event - O(1), never blocks, drops oldest if full
    #[inline]
    pub fn push(&self, event: AuditEvent) {
        let mut buffer = self.buffer.lock();

        if buffer.len() >= self.capacity {
            buffer.pop_front(); // Drop oldest
        }

        buffer.push_back(event);
    }

    /// Drain all events - returns ownership for async writer
    pub fn drain(&self) -> Vec<AuditEvent> {
        let mut buffer = self.buffer.lock();
        buffer.drain(..).collect()
    }

    /// Current buffer size
    pub fn len(&self) -> usize {
        self.buffer.lock().len()
    }

    pub fn is_empty(&self) -> bool {
        self.buffer.lock().is_empty()
    }
}

impl AuditEvent {
    /// Create new audit event with current timestamp
    pub fn new(
        event_type: AuditEventType,
        module: &str,
        severity: Severity,
        message: &str,
    ) -> Self {
        Self {
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0),
            event_type,
            module: module.to_string(),
            severity,
            message: message.to_string(),
            caller_file: None,
            caller_line: None,
        }
    }

    pub fn with_caller(mut self, file: Option<String>, line: Option<u32>) -> Self {
        self.caller_file = file;
        self.caller_line = line;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ring_buffer_push() {
        let buffer = AuditRingBuffer::new(3);

        for i in 0..5 {
            buffer.push(AuditEvent::new(
                AuditEventType::ImportAllowed,
                &format!("module{}", i),
                Severity::Low,
                "test",
            ));
        }

        // Should only have last 3 events
        assert_eq!(buffer.len(), 3);
    }

    #[test]
    fn test_ring_buffer_drain() {
        let buffer = AuditRingBuffer::new(10);

        buffer.push(AuditEvent::new(
            AuditEventType::ImportBlocked,
            "blocked_module",
            Severity::High,
            "Blocked by policy",
        ));

        let events = buffer.drain();
        assert_eq!(events.len(), 1);
        assert!(buffer.is_empty());
    }
}
