describe('agendalink — smoke', () => {
  it('loads the landing page', () => {
    cy.visit('/', { timeout: 60_000 });
    cy.contains('h1', 'Agendamentos sem complicação');
    cy.contains('a', 'Começar agora').should('be.visible');
  });

  it('loads the login page', () => {
    cy.visit('/auth/login/');
    cy.contains('h1', 'Entrar');
    cy.get('#id_username').should('be.visible');
    cy.get('#id_password').should('be.visible');
  });

  it('loads the registration page', () => {
    cy.visit('/auth/cadastro/');
    cy.contains('h1', 'Criar conta');
  });

  it('API health via products list', () => {
    cy.request('/api/products/').its('status').should('eq', 200);
  });
});
