Cypress.Commands.add('loginAsProfessional', () => {
  cy.fixture('e2e').then((data) => {
    cy.session(
      `prof-${data.professional.username}`,
      () => {
        cy.visit('/auth/login/', { timeout: 60_000 });
        cy.get('#id_username').clear().type(data.professional.username);
        cy.get('#id_password').clear().type(data.professional.password, { log: false });
        cy.get('button[type=submit]').click();
        cy.url({ timeout: 15_000 }).should('include', '/dashboard/');
      },
      { cacheAcrossSpecs: true },
    );
  });
});

Cypress.Commands.add('getE2eProductId', () => {
  return cy.request('/api/products/').then((response) => {
    expect(response.status).to.eq(200);
    const products = response.body.products || [];
    const product = products.find((p) => p.name === 'Serviço E2E');
    expect(product, 'seed product Serviço E2E').to.exist;
    return product.id;
  });
});

Cypress.Commands.add('typeChatInput', (text) => {
  cy.get('#chatTextInput', { timeout: 15_000 }).should('be.visible').clear().type(text);
  cy.get('#chatSendBtn').click();
});

Cypress.Commands.add('pickChatOption', (labelPart) => {
  cy.contains('button.opcao-btn', labelPart, { timeout: 15_000 }).click();
});
