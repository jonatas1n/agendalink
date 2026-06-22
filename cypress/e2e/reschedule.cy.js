describe('Sugerir remarcação — UI da agenda', () => {
  beforeEach(() => {
    cy.loginAsProfessional();
  });

  it('exibe slots ao selecionar dia no calendário', () => {
    cy.visit('/appointments/', { timeout: 60_000 });
    cy.get('.appointment-options-btn').first().click();
    cy.get('#appointmentSuggestLink').click();
    cy.get('#calendarMount .cal-day', { timeout: 15_000 })
      .not('.cal-passado')
      .not('.cal-indisponivel')
      .not('.cal-vazio')
      .first()
      .click();
    cy.get('#slotsMount .slot-btn', { timeout: 10_000 }).should('have.length.at.least', 1);
  });
});
