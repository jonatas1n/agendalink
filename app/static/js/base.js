// Auto-dismiss messages after 4s
document.querySelectorAll('.message').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

/**
 * Brazilian currency mask (centavos while typing).
 * Use data-currency on inputs or call initCurrencyInputs(container).
 */
function formatCurrencyInputDigits(digits) {
  if (!digits) return '';
  const num = parseInt(digits, 10) / 100;
  return num.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function normalizeInitialCurrencyValue(value) {
  const raw = String(value || '').trim();
  if (!raw) return '';
  if (raw.includes(',')) {
    return formatCurrencyInputDigits(raw.replace(/\D/g, ''));
  }
  const n = parseFloat(raw.replace(',', '.'));
  if (Number.isNaN(n)) return '';
  return formatCurrencyInputDigits(String(Math.round(n * 100)));
}

function bindCurrencyInput(input) {
  if (input.dataset.currencyBound === '1') return;
  input.dataset.currencyBound = '1';
  input.setAttribute('inputmode', 'decimal');
  input.setAttribute('autocomplete', 'off');
  if (input.value) {
    input.value = normalizeInitialCurrencyValue(input.value);
  }
  input.addEventListener('input', () => {
    const digits = input.value.replace(/\D/g, '');
    input.value = formatCurrencyInputDigits(digits);
  });
}

function initCurrencyInputs(root) {
  const scope = root && root.querySelectorAll ? root : document;
  scope.querySelectorAll('[data-currency]').forEach(bindCurrencyInput);
}

window.AgendaFacil = window.AgendaFacil || {};
window.AgendaFacil.initCurrencyInputs = initCurrencyInputs;
window.AgendaFacil.formatCurrencyInputDigits = formatCurrencyInputDigits;
/** Resposta JSON de erro da API pública (chave `erro`, legado `error`). */
window.AgendaFacil.mensagemErroApi = function (data) {
  if (!data || typeof data !== 'object') return '';
  return data.erro || data.error || '';
};

document.addEventListener('DOMContentLoaded', () => initCurrencyInputs(document));
