describe('API pública JSON', () => {
  it('lista produtos ativos', () => {
    cy.request('/api/products/').then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.products).to.be.an('array');
      expect(res.body.products.length).to.be.greaterThan(0);
    });
  });

  it('retorna detalhe e disponibilidade do produto E2E', () => {
    cy.getE2eProductId().then((id) => {
      cy.request(`/api/products/${id}/`).its('status').should('eq', 200);
      cy.request(`/api/products/${id}/availability/`).then((res) => {
        expect(res.status).to.eq(200);
        expect(res.body.availability).to.be.an('object');
        const dates = Object.keys(res.body.availability);
        expect(dates.length).to.be.greaterThan(0);
      });
    });
  });

  it('check availability exige parâmetros', () => {
    cy.request({
      url: '/api/appointments/check/',
      failOnStatusCode: false,
    }).its('status').should('eq', 400);
  });
});
