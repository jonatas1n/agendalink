describe('Autenticação', () => {
  it('rejeita login com credenciais inválidas', () => {
    cy.visit('/auth/login/', { timeout: 60_000 });
    cy.get('#id_username').type('usuario_inexistente');
    cy.get('#id_password').type('senha_errada');
    cy.get('button[type=submit]').click();
    cy.contains('.message--error', 'incorretos');
    cy.url().should('include', '/auth/login/');
  });

  it('entra com usuário E2E seed', () => {
    cy.fixture('e2e').then((data) => {
      cy.visit('/auth/login/');
      cy.get('#id_username').type(data.professional.username);
      cy.get('#id_password').type(data.professional.password);
      cy.get('button[type=submit]').click();
      cy.url({ timeout: 15_000 }).should('include', '/dashboard/');
      cy.contains('h1', /Olá/);
    });
  });

  it('redireciona cadastro para dashboard se já logado', () => {
    cy.loginAsProfessional();
    cy.visit('/auth/cadastro/');
    cy.url({ timeout: 10_000 }).should('include', '/dashboard/');
  });

  it('formulário de cadastro exibe campos principais', () => {
    cy.visit('/auth/cadastro/');
    cy.get('#id_username').should('exist');
    cy.get('#id_email').should('exist');
    cy.get('#id_password1').should('exist');
    cy.get('#id_password2').should('exist');
  });
});
