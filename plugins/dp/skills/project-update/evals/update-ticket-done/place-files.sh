#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
# Fixture dotfiles are stored without the dot, so they don't act on the repo that holds the evals.
[ -f gitignore ] && mv gitignore .gitignore
[ -d github ] && mv github .github
git init -q -b main
git add -A
git -c user.name=Eval -c user.email=eval@example.com commit -qm "Initial commit"
cat > limiter.go <<'EOF'
package proxy

import (
	"net/http"
	"strconv"
	"sync"
	"time"
)

// Limiter is a per-client token-bucket rate limiter.
type Limiter struct {
	mu      sync.Mutex
	rate    float64 // tokens per second
	burst   float64
	buckets map[string]*bucket
	now     func() time.Time
}

type bucket struct {
	tokens float64
	last   time.Time
}

func NewLimiter(rate, burst float64) *Limiter {
	return &Limiter{rate: rate, burst: burst, buckets: map[string]*bucket{}, now: time.Now}
}

// Allow reports whether client may make a request now, and if not, how long to wait.
func (l *Limiter) Allow(client string) (bool, time.Duration) {
	l.mu.Lock()
	defer l.mu.Unlock()
	t := l.now()
	b, ok := l.buckets[client]
	if !ok {
		b = &bucket{tokens: l.burst, last: t}
		l.buckets[client] = b
	}
	b.tokens = min(l.burst, b.tokens+t.Sub(b.last).Seconds()*l.rate)
	b.last = t
	if b.tokens >= 1 {
		b.tokens--
		return true, 0
	}
	return false, time.Duration((1 - b.tokens) / l.rate * float64(time.Second))
}

// Middleware rejects over-limit requests with 429 and a Retry-After header.
func (l *Limiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if ok, wait := l.Allow(r.RemoteAddr); !ok {
			w.Header().Set("Retry-After", strconv.Itoa(int(wait.Seconds())+1))
			http.Error(w, "rate limited", http.StatusTooManyRequests)
			return
		}
		next.ServeHTTP(w, r)
	})
}
EOF
cat > limiter_test.go <<'EOF'
package proxy

import (
	"testing"
	"time"
)

func TestRefill(t *testing.T) {
	now := time.Unix(0, 0)
	l := NewLimiter(10, 1)
	l.now = func() time.Time { return now }
	if ok, _ := l.Allow("a"); !ok {
		t.Fatal("first request should pass")
	}
	if ok, _ := l.Allow("a"); ok {
		t.Fatal("second request should be limited")
	}
	now = now.Add(100 * time.Millisecond)
	if ok, _ := l.Allow("a"); !ok {
		t.Fatal("bucket should refill after 100ms at 10/s")
	}
}
EOF
git add limiter.go limiter_test.go
git -c user.name=Eval -c user.email=eval@example.com commit -qm "Add token-bucket rate limiter (T-007)"
