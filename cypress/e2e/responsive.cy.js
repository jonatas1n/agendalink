describe('agendalink — responsive layout', () => {
  const viewports = [
    { label: 'mobile', width: 390, height: 844 },
    { label: 'tablet', width: 768, height: 1024 },
  ];

  viewports.forEach(({ label, width, height }) => {
    it(`landing renders on ${label}`, () => {
      cy.viewport(width, height);
      cy.visit('/', { timeout: 60_000 });
      cy.contains('h1', 'Agendamentos sem complicação').should('be.visible');
    });

    it(`dashboard table scrolls on ${label}`, () => {
      cy.viewport(width, height);
      cy.loginAsProfessional();
      cy.visit('/dashboard/', { timeout: 60_000 });
      cy.get('.table-scroll').should('be.visible');
      cy.contains('td', 'Cliente E2E Seed');
    });
  });
});
