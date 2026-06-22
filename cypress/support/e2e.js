import './commands';

// Avoid hanging page load in Docker/CI when external fonts are slow or blocked.
beforeEach(() => {
  cy.intercept('GET', '**/fonts.googleapis.com/**', { statusCode: 200, body: '/* stub */' });
  cy.intercept('GET', '**/fonts.gstatic.com/**', { statusCode: 200, body: '' });
});
