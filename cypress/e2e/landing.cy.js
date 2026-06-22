describe('Landing e navegação pública', () => {
  it('exibe hero e seção como funciona', () => {
    cy.visit('/', { timeout: 60_000 });
    cy.contains('h1', 'Agendamentos sem complicação');
    cy.get('#como-funciona').should('exist');
    cy.contains('a', 'Começar agora').should('have.attr', 'href', '/auth/cadastro/');
  });

  it('header leva ao login quando deslogado', () => {
    cy.visit('/');
    cy.contains('.site-nav a', 'Entrar').click();
    cy.url().should('include', '/auth/login/');
  });

  it('footer está visível', () => {
    cy.visit('/');
    cy.get('.site-footer').should('be.visible');
  });
});
