(function () {
  const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]{1,78}[a-z0-9])?$/;
  const MAX_SLUG_LENGTH = 80;

  function messageForKind(kind) {
    switch (kind) {
      case 'space':
        return 'Espaços não são permitidos. Use hífen (-) entre palavras.';
      case 'whitespace':
        return 'Não use espaços ou quebras de linha no endereço.';
      case 'accent':
        return 'Caracteres acentuados não são permitidos. Use letras de a a z sem acento.';
      case 'leading_hyphen':
        return 'O endereço deve começar com letra ou número, não com hífen.';
      case 'double_hyphen':
        return 'Não use dois hífens seguidos.';
      case 'max_length':
        return 'O endereço pode ter no máximo 80 caracteres.';
      default:
        return 'Este caractere não é permitido. Use letras minúsculas, números e hífens.';
    }
  }

  function classifyChar(ch) {
    if (ch >= 'A' && ch <= 'Z') {
      return { kind: 'upper', as: ch.toLowerCase() };
    }
    if (ch >= 'a' && ch <= 'z') {
      return { kind: 'ok', as: ch };
    }
    if (ch >= '0' && ch <= '9') {
      return { kind: 'ok', as: ch };
    }
    if (ch === '-') {
      return { kind: 'hyphen' };
    }
    if (ch === ' ') {
      return { kind: 'space' };
    }
    if (/\s/u.test(ch)) {
      return { kind: 'whitespace' };
    }
    const decomposed = ch.normalize('NFD');
    if (decomposed !== ch && /\p{M}/u.test(decomposed)) {
      return { kind: 'accent' };
    }
    const base = decomposed.replace(/\p{M}/gu, '');
    if (base !== ch && /[a-zA-Z]/.test(base)) {
      return { kind: 'accent' };
    }
    return { kind: 'invalid' };
  }

  /**
   * Mantém só caracteres permitidos; retorna mensagem do primeiro caractere rejeitado.
   */
  function sanitizeSlugInput(raw) {
    let result = '';
    let message = null;

    for (const ch of String(raw || '')) {
      if (result.length >= MAX_SLUG_LENGTH) {
        if (!message) {
          message = messageForKind('max_length');
        }
        continue;
      }

      const cls = classifyChar(ch);
      if (cls.kind === 'upper' || cls.kind === 'ok') {
        result += cls.as;
        continue;
      }
      if (cls.kind === 'hyphen') {
        if (result.length === 0) {
          if (!message) {
            message = messageForKind('leading_hyphen');
          }
          continue;
        }
        if (result.endsWith('-')) {
          if (!message) {
            message = messageForKind('double_hyphen');
          }
          continue;
        }
        result += '-';
        continue;
      }
      if (!message) {
        message = messageForKind(cls.kind);
      }
    }

    return { value: result, message };
  }

  function normalizeStoreSlug(raw) {
    const trimmed = String(raw || '').trim().toLowerCase();
    if (!trimmed) return '';
    return trimmed
      .normalize('NFD')
      .replace(/\p{M}/gu, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  function validateStoreSlugSync(raw, reservedSlugs) {
    const slug = normalizeStoreSlug(raw);
    if (slug.length < 3) {
      return {
        ok: false,
        message: 'Use pelo menos 3 caracteres (letras, números ou hífens).',
      };
    }
    if (slug.length > MAX_SLUG_LENGTH) {
      return { ok: false, message: messageForKind('max_length') };
    }
    if (!SLUG_RE.test(slug)) {
      return {
        ok: false,
        message: 'Use apenas letras minúsculas, números e hífens.',
      };
    }
    const reserved = reservedSlugs instanceof Set
      ? reservedSlugs
      : new Set(reservedSlugs || []);
    if (reserved.has(slug)) {
      return { ok: false, message: 'Este endereço não está disponível.' };
    }
    return { ok: true, slug };
  }

  function readConfig() {
    const el = document.getElementById('storeSlugValidationConfig');
    if (!el) return null;
    try {
      return JSON.parse(el.textContent || '');
    } catch (e) {
      console.error(e);
      return null;
    }
  }

  function setClientError(errorEl, message) {
    if (!errorEl) return;
    if (message) {
      errorEl.textContent = message;
      errorEl.hidden = false;
    } else {
      errorEl.textContent = '';
      errorEl.hidden = true;
    }
  }

  function applySanitizedValue(input, sanitized, errorEl) {
    if (input.value === sanitized.value) {
      if (sanitized.message) {
        setClientError(errorEl, sanitized.message);
      }
      return sanitized.value.length;
    }
    const start = input.selectionStart;
    const prevLen = input.value.length;
    input.value = sanitized.value;
    if (sanitized.message) {
      setClientError(errorEl, sanitized.message);
    }
    const delta = sanitized.value.length - prevLen;
    const nextPos = Math.max(0, Math.min(sanitized.value.length, (start ?? sanitized.value.length) + delta));
    try {
      input.setSelectionRange(nextPos, nextPos);
    } catch (e) {
      /* input type may not support selection */
    }
    return nextPos;
  }

  function bindSlugLiveInput(input, errorEl) {
    if (!input || input.dataset.slugLiveBound === '1') return;
    input.dataset.slugLiveBound = '1';

    input.addEventListener('beforeinput', (event) => {
      if (event.isComposing) return;
      const type = event.inputType || '';
      if (type.startsWith('delete') || type === 'historyUndo' || type === 'historyRedo') {
        return;
      }

      const data = event.data;
      if (data == null || data === '') {
        return;
      }

      const start = input.selectionStart ?? input.value.length;
      const end = input.selectionEnd ?? start;
      const before = input.value.slice(0, start);
      const after = input.value.slice(end);
      const sanitized = sanitizeSlugInput(before + data + after);
      const wouldBe = before + data + after;

      if (sanitized.value === wouldBe) {
        if (sanitized.message) {
          setClientError(errorEl, sanitized.message);
        }
        return;
      }

      event.preventDefault();
      applySanitizedValue(input, sanitized, errorEl);
    });

    input.addEventListener('input', (event) => {
      if (event.isComposing) return;
      const sanitized = sanitizeSlugInput(input.value);
      if (sanitized.value !== input.value || sanitized.message) {
        applySanitizedValue(input, sanitized, errorEl);
        return;
      }
      setClientError(errorEl, '');
    });

    input.addEventListener('paste', (event) => {
      event.preventDefault();
      const pasted = event.clipboardData?.getData('text') || '';
      const start = input.selectionStart ?? input.value.length;
      const end = input.selectionEnd ?? start;
      const before = input.value.slice(0, start);
      const after = input.value.slice(end);
      const sanitized = sanitizeSlugInput(before + pasted + after);
      applySanitizedValue(input, sanitized, errorEl);
    });
  }

  function bindStoreSlugForm(form) {
    if (!form || form.dataset.storeSlugBound === '1') return;
    const config = readConfig();
    if (!config) return;

    form.dataset.storeSlugBound = '1';
    const input = form.querySelector('#id_slug');
    const errorEl = form.querySelector('[data-slug-client-error]');
    if (!input) return;

    bindSlugLiveInput(input, errorEl);

    const reserved = new Set(config.reserved || []);

    function runSyncValidation() {
      const result = validateStoreSlugSync(input.value, reserved);
      if (!result.ok) {
        setClientError(errorEl, result.message);
        return result;
      }
      setClientError(errorEl, '');
      return result;
    }

    input.addEventListener('blur', () => {
      const sanitized = sanitizeSlugInput(input.value);
      if (sanitized.value !== input.value) {
        input.value = sanitized.value;
      }
      const result = runSyncValidation();
      if (result.ok && result.slug !== input.value.trim()) {
        input.value = result.slug;
      }
    });

    form.addEventListener('submit', (event) => {
      const live = sanitizeSlugInput(input.value);
      if (live.value !== input.value) {
        input.value = live.value;
      }

      const sync = runSyncValidation();
      if (!sync.ok) {
        event.preventDefault();
        input.focus();
        return;
      }

      if (!config.checkUrl) {
        input.value = sync.slug;
        return;
      }

      event.preventDefault();
      const submitBtn = form.querySelector('[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const url = new URL(config.checkUrl, window.location.origin);
      url.searchParams.set('slug', input.value);

      fetch(url.toString(), {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      })
        .then(async (response) => {
          const data = await response.json().catch(() => ({}));
          if (!response.ok || !data.ok) {
            const msg =
              (window.agendalink && window.agendalink.mensagemErroApi(data)) ||
              data.erro ||
              'Não foi possível validar o endereço. Tente novamente.';
            setClientError(errorEl, msg);
            input.focus();
            return;
          }
          input.value = data.slug || sync.slug;
          setClientError(errorEl, '');
          form.submit();
        })
        .catch((e) => {
          console.error(e);
          setClientError(
            errorEl,
            'Não foi possível validar o endereço. Verifique sua conexão.',
          );
          input.focus();
        })
        .finally(() => {
          if (submitBtn) submitBtn.disabled = false;
        });
    });
  }

  window.agendalink = window.agendalink || {};
  window.agendalink.normalizeStoreSlug = normalizeStoreSlug;
  window.agendalink.validateStoreSlugSync = validateStoreSlugSync;
  window.agendalink.sanitizeSlugInput = sanitizeSlugInput;
  window.agendalink.bindStoreSlugForm = bindStoreSlugForm;

  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('storeSettingsForm');
    bindStoreSlugForm(form);
  });
})();
