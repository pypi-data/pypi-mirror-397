//! Circuit breaker for graceful degradation.

use parking_lot::RwLock;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CircuitState {
    Closed,
    Open,
    HalfOpen,
}

/// Circuit breaker for external service calls (e.g., Atlas queries)
pub struct CircuitBreaker {
    state: RwLock<CircuitState>,
    failure_count: AtomicUsize,
    failure_threshold: usize,
    recovery_timeout: Duration,
    last_failure_time: RwLock<Option<Instant>>,
}

impl CircuitBreaker {
    /// Create new circuit breaker
    pub fn new(failure_threshold: usize, recovery_timeout: Duration) -> Self {
        Self {
            state: RwLock::new(CircuitState::Closed),
            failure_count: AtomicUsize::new(0),
            failure_threshold,
            recovery_timeout,
            last_failure_time: RwLock::new(None),
        }
    }

    /// Execute function with circuit breaker protection
    pub fn call<T, E, F>(&self, f: F) -> Result<T, CircuitBreakerError<E>>
    where
        F: FnOnce() -> Result<T, E>,
    {
        // Check if circuit is open
        if self.is_open() {
            return Err(CircuitBreakerError::Open);
        }

        // Try half-open transition
        if *self.state.read() == CircuitState::Open {
            if self.should_attempt_reset() {
                *self.state.write() = CircuitState::HalfOpen;
            } else {
                return Err(CircuitBreakerError::Open);
            }
        }

        // Execute function
        match f() {
            Ok(result) => {
                self.on_success();
                Ok(result)
            }
            Err(e) => {
                self.on_failure();
                Err(CircuitBreakerError::Failure(e))
            }
        }
    }

    /// Check if circuit is currently open
    pub fn is_open(&self) -> bool {
        let state = *self.state.read();
        state == CircuitState::Open && !self.should_attempt_reset()
    }

    /// Get current state
    pub fn state(&self) -> CircuitState {
        *self.state.read()
    }

    fn on_success(&self) {
        self.failure_count.store(0, Ordering::SeqCst);
        *self.state.write() = CircuitState::Closed;
    }

    fn on_failure(&self) {
        let count = self.failure_count.fetch_add(1, Ordering::SeqCst) + 1;
        *self.last_failure_time.write() = Some(Instant::now());

        if count >= self.failure_threshold {
            *self.state.write() = CircuitState::Open;
        }
    }

    fn should_attempt_reset(&self) -> bool {
        if let Some(last_failure) = *self.last_failure_time.read() {
            last_failure.elapsed() >= self.recovery_timeout
        } else {
            true
        }
    }
}

#[derive(Debug)]
pub enum CircuitBreakerError<E> {
    Open,
    Failure(E),
}

impl<E: std::fmt::Display> std::fmt::Display for CircuitBreakerError<E> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Open => write!(f, "Circuit breaker is open"),
            Self::Failure(e) => write!(f, "Operation failed: {}", e),
        }
    }
}

impl<E: std::error::Error> std::error::Error for CircuitBreakerError<E> {}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[test]
    fn test_circuit_closed_initially() {
        let cb = CircuitBreaker::new(3, Duration::from_secs(30));
        assert_eq!(cb.state(), CircuitState::Closed);
    }

    #[test]
    fn test_circuit_opens_after_failures() {
        let cb = CircuitBreaker::new(3, Duration::from_secs(30));

        for _ in 0..3 {
            let _ = cb.call::<(), _, _>(|| Err::<(), _>("error"));
        }

        assert_eq!(cb.state(), CircuitState::Open);
    }

    #[test]
    fn test_circuit_rejects_when_open() {
        let cb = CircuitBreaker::new(1, Duration::from_secs(30));

        let _ = cb.call::<(), &str, _>(|| Err::<(), _>("error"));

        let result: Result<(), CircuitBreakerError<&str>> = cb.call::<(), &str, _>(|| Ok(()));
        assert!(matches!(result, Err(CircuitBreakerError::Open)));
    }

    #[test]
    fn test_circuit_resets_on_success() {
        let cb = CircuitBreaker::new(3, Duration::from_secs(30));

        // 2 failures (below threshold)
        let _ = cb.call::<(), _, _>(|| Err::<(), _>("error"));
        let _ = cb.call::<(), _, _>(|| Err::<(), _>("error"));

        // 1 success resets count
        let _ = cb.call::<(), &str, _>(|| Ok(()));

        assert_eq!(cb.state(), CircuitState::Closed);
    }
}
