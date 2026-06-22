describe('Fluxo de agendamento conversacional', () => {
  it('carrega página pública de agendar', () => {
    cy.getE2eProductId().then((productId) => {
      cy.visit(`/products/${productId}/book/`, { timeout: 60_000 });
      cy.contains('.chat-aside', 'Serviço E2E');
      cy.get('.booking-product-list').should('exist');
      cy.get('#chatBox').should('exist');
    });
  });

  it('completa agendamento como visitante (até confirmação API)', () => {
    cy.fixture('e2e').then((data) => {
      cy.getE2eProductId().then((productId) => {
        cy.intercept('POST', '/api/appointments/create/').as('createAppointment');

        cy.visit(`/products/${productId}/book/`);

        cy.contains('.balao-bot', 'e-mail', { timeout: 20_000 });

        cy.typeChatInput('Maria E2E Teste');
        cy.typeChatInput(data.validCpf);
        cy.typeChatInput(data.guestEmail);

        cy.pickChatOption('Só e-mail');
        cy.contains('.balao-bot', 'data', { timeout: 20_000 });

        cy.get('.mini-cal .cal-day', { timeout: 20_000 })
          .not('.cal-passado')
          .not('.cal-indisponivel')
          .not('.cal-vazio')
          .first()
          .click();

        cy.get('.slot-btn', { timeout: 15_000 }).first().click();

        cy.pickChatOption('Confirmar');

        cy.wait('@createAppointment', { timeout: 30_000 }).then((interception) => {
          expect(interception.response.statusCode).to.eq(201);
        });

        cy.contains('.balao-bot', 'confirmado', { timeout: 15_000 });
      });
    });
  });
});
