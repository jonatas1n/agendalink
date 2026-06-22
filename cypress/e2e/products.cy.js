describe('Serviços — profissional', () => {
  beforeEach(() => {
    cy.loginAsProfessional();
  });

  it('abre formulário de novo serviço', () => {
    cy.visit('/products/new/', { timeout: 60_000 });
    cy.contains('h1', 'Novo serviço');
    cy.get('input[name=name]').should('be.visible');
    cy.get('#produtoForm').should('exist');
  });

  it('cria serviço com preço e vai para horários', () => {
    const unique = `Corte E2E ${Date.now()}`;
    cy.visit('/products/new/');
    cy.get('input[name=name]').type(unique);
    cy.get('textarea[name=description]').type('Descrição teste E2E');
    cy.get('input[name=price_amount]').first().clear().type('150,00');
    cy.get('button[type=submit]').click();
    cy.url({ timeout: 15_000 }).should('match', /\/products\/\d+\/availability\//);
    cy.contains('h1', 'Horários disponíveis');
  });

  it('salva horários semanais', () => {
    cy.getE2eProductId().then((productId) => {
      cy.visit(`/products/${productId}/availability/`);
      cy.get('#dispForm').within(() => {
        cy.get('select[name=weekday]').first().select('0');
        cy.get('input[name=start_time]').first().clear().type('09:00');
        cy.get('input[name=end_time]').first().clear().type('17:00');
        cy.contains('button[type=submit]', 'Salvar horários').click();
      });
      cy.url({ timeout: 15_000 }).should('include', '/dashboard/');
      cy.contains('.message--success', 'Disponibilidade salva');
    });
  });

  it('edita serviço seed', () => {
    cy.getE2eProductId().then((productId) => {
      cy.visit(`/products/${productId}/edit/`);
      cy.contains('h1', /Editar|serviço/i);
      cy.get('input[name=name]').should('have.value', 'Serviço E2E');
    });
  });
});
