describe('Painel do profissional', () => {
  beforeEach(() => {
    cy.loginAsProfessional();
  });

  it('lista serviço seed e link de agendamento', () => {
    cy.visit('/dashboard/', { timeout: 60_000 });
    cy.contains('.servico-card', 'Serviço E2E');
    cy.get('#btnLinkAgendamento').should('exist');
    cy.contains('a', 'Definições da loja').should('have.attr', 'href').and('include', '/dashboard/store/');
  });

  it('abre modal de link de agendamento e copia', () => {
    cy.visit('/dashboard/');
    cy.contains('#btnLinkAgendamento', 'Link de agendamento').click();
    cy.get('#bookingLinkModal').should('not.have.attr', 'hidden');
    cy.get('#bookingLinkInput').should('be.visible').and('not.be.empty');
    cy.get('#bookingLinkCopiedNotice').should('not.be.hidden');
    cy.get('#btnCopyBookingLink').click();
    cy.get('#bookingLinkCopiedNotice').should('not.be.hidden');
  });

  it('mostra agendamento seed na tabela', () => {
    cy.visit('/dashboard/');
    cy.contains('td', 'Cliente E2E Seed');
    cy.contains('td', 'Serviço E2E');
  });

  it('abre modal de detalhes do agendamento', () => {
    cy.visit('/dashboard/');
    cy.get('.appointment-options-btn').first().click();
    cy.get('#appointmentModal').should('not.have.attr', 'hidden');
    cy.contains('#modalName', 'Cliente E2E Seed');
    cy.get('#appointmentSuggestLink').should('be.visible');
  });
});
