# Pre-Deployment Checklist

Use this checklist before deploying to production.

## Testing

### Unit Tests
- [ ] All unit tests pass
  ```bash
  pytest backend/services/*.test.py backend/api/routes/*.test.py -v
  ```
- [ ] Code coverage >= 80%
  ```bash
  pytest backend/tests/ --cov=backend --cov-report=term
  ```

### Integration Tests
- [ ] All integration tests pass
  ```bash
  pytest backend/tests/integration/ -v
  ```
- [ ] End-to-end chat flow works
- [ ] Error handling works correctly
- [ ] Fallback mechanisms work

### Accuracy Tests
- [ ] Accuracy tests pass
  ```bash
  pytest backend/tests/accuracy/ -v
  ```
- [ ] Response accuracy >= 80%
- [ ] Keywords present in responses
- [ ] Sources are relevant

### Compliance Tests
- [ ] Compliance tests pass
  ```bash
  pytest backend/tests/compliance/ -v
  ```
- [ ] No investment advice generated
- [ ] Blocked queries are blocked
- [ ] Allowed queries are allowed

### Load Tests
- [ ] Load tests pass
  ```bash
  python -m backend.tests.load.run_load_tests --scenario medium_load
  ```
- [ ] Success rate >= 95%
- [ ] P95 response time < 5 seconds
- [ ] Error rate < 5%
- [ ] System handles concurrent requests

## Code Quality

- [ ] Code passes linting
  ```bash
  flake8 backend/
  ```
- [ ] Code formatted correctly
  ```bash
  black --check backend/
  ```
- [ ] Type hints checked
  ```bash
  mypy backend/
  ```
- [ ] No TODO comments in production code
- [ ] No debug print statements
- [ ] No hardcoded secrets

## Configuration

### Environment Variables
- [ ] All required environment variables set
- [ ] No default/test values in production
- [ ] API keys configured securely
- [ ] Database connection strings correct
- [ ] CORS origins configured correctly

### Settings
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Rate limiting enabled
- [ ] Monitoring enabled

## Database

- [ ] Vector database initialized
- [ ] Test data loaded
- [ ] Database backups configured
- [ ] Migration scripts tested
- [ ] Database connection pooling configured

## Security

- [ ] API keys secured (not in code)
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation working
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] HTTPS enabled
- [ ] SSL certificate valid

## Monitoring

- [ ] Monitoring service configured
- [ ] Alerts configured
- [ ] Logging configured
- [ ] Dashboard accessible
- [ ] Error tracking working
- [ ] Performance metrics collected

## Documentation

- [ ] API documentation updated
- [ ] README updated
- [ ] Deployment guide updated
- [ ] Testing guide updated
- [ ] Environment variables documented
- [ ] Architecture documented

## Deployment

### Backend
- [ ] Backend server starts successfully
- [ ] Health check endpoint works
- [ ] Ready endpoint works
- [ ] All API endpoints accessible
- [ ] Database connections work
- [ ] External API calls work

### Frontend
- [ ] Frontend builds successfully
- [ ] Static assets served correctly
- [ ] API calls work
- [ ] Error handling works
- [ ] Loading states work
- [ ] Responsive design verified

### Infrastructure
- [ ] Server resources adequate
- [ ] Load balancer configured
- [ ] Auto-scaling configured (if applicable)
- [ ] CDN configured (if applicable)
- [ ] Domain name configured
- [ ] SSL certificate installed

## Rollback Plan

- [ ] Rollback procedure documented
- [ ] Previous version tagged
- [ ] Database migration rollback tested
- [ ] Rollback script tested

## Communication

- [ ] Team notified of deployment
- [ ] Maintenance window scheduled (if needed)
- [ ] Stakeholders informed
- [ ] Support team briefed

## Post-Deployment

- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify functionality
- [ ] Test critical paths
- [ ] Monitor user feedback
- [ ] Check alert notifications

## Emergency Contacts

- [ ] On-call engineer contact info available
- [ ] Escalation path documented
- [ ] Support channels accessible

## Sign-Off

- [ ] Technical lead approval
- [ ] QA approval
- [ ] Security review completed
- [ ] Product owner approval

---

**Date:** _______________

**Deployed by:** _______________

**Version:** _______________

**Notes:** _______________

