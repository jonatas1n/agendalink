describe('Proteção de rotas autenticadas', () => {
  it('dashboard exige login', () => {
    cy.visit('/dashboard/', { timeout: 60_000, failOnStatusCode: false });
    cy.url().should('include', '/auth/login/');
  });

  it('novo produto exige login', () => {
    cy.visit('/products/new/', { failOnStatusCode: false });
    cy.url().should('include', '/auth/login/');
  });

  it('lista de agendamentos exige login', () => {
    cy.visit('/appointments/', { failOnStatusCode: false });
    cy.url().should('include', '/auth/login/');
  });
});
