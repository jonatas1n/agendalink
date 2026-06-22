describe('Modal de agendamento', () => {
  beforeEach(() => {
    cy.loginAsProfessional();
    cy.visit('/dashboard/');
  });

  it('fecha com botão ou backdrop', () => {
    cy.get('.appointment-options-btn').first().click();
    cy.get('#appointmentModal').should('not.have.attr', 'hidden');
    cy.get('.appointment-modal__backdrop').click({ force: true });
    cy.get('#appointmentModal').should('have.attr', 'hidden');
  });

  it('mostra dados do cliente seed no modal', () => {
    cy.get('.appointment-options-btn').first().click();
    cy.contains('#modalEmail', '@');
    cy.contains('#modalService', 'Serviço E2E');
  });
});
