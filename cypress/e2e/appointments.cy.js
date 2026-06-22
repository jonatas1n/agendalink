describe('Agendamentos (HTML)', () => {
  beforeEach(() => {
    cy.loginAsProfessional();
  });

  it('lista agendamentos do profissional', () => {
    cy.visit('/appointments/', { timeout: 60_000 });
    cy.contains('h1', 'Meus agendamentos');
    cy.contains('td', 'Cliente E2E Seed');
  });

  it('abre tela de sugerir remarcação', () => {
    cy.visit('/appointments/');
    cy.get('.appointment-options-btn').first().click();
    cy.get('#appointmentSuggestLink').click();
    cy.url().should('include', '/suggest-reschedule/');
    cy.contains('h1', 'Sugerir remarcação');
    cy.contains('Horário atualmente marcado');
    cy.get('#calendarMount').should('exist');
  });
});
